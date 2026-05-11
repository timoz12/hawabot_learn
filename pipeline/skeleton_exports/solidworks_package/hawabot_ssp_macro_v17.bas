Attribute VB_Name = "HawaBotSSP"
' ============================================================================
' HawaBot Pro - Skeleton Sketch Part (SSP) Builder Macro - v17
' SolidWorks 2025
'
' v17 = v16 + GEOMETRY FIXES + POPPY-INFORMED PROPORTIONS + DOF CHANGES
'
' Tier A geometry bug fixes (all):
'   - Added PL_ELBOW_Z (Z=100) and PL_HAND_Z (Z=50) horizontal planes.
'     Previous arm axes used PL_SHOULDER as the second reference, putting
'     elbow and hand axes at shoulder height (Z=140). Now corrected.
'   - Hip yaw and hip pitch were the same line (both = PL_HIP n PL_*_HIP).
'     Now AX_*_HIP_YAW = PL_*_HIP n Front Plane (vertical Z line, correct
'     for yaw rotation), AX_*_HIP_PITCH = PL_HIP n Front Plane (X-direction
'     line, correct for pitch rotation).
'   - All "yaw" axes (head pan, waist yaw, hip yaw) now correctly oriented
'     as vertical lines (intersection of two vertical planes).
'   - Hand X separated from elbow X (PL_*_HAND now at X=+/-55, was +/-65 same
'     as elbow).
'
' Tier B proportion changes (Poppy-informed):
'   - SHOULDER_X: 48 -> 40    (narrower shoulders)
'   - ELBOW_X:    65 -> 75    (longer outward reach)
'   - ELBOW_Z:    105 -> 100  (drops elbow slightly)
'   - HAND_X:     new = 55    (hand inward of elbow, slight forward bend)
'   - HAND_Z:     70 -> 50    (longer forearm, Poppy ratio)
'   - KNEE_Z:     -60 -> -55  (slightly higher knee)
'   - ANKLE_Z:    -105 -> -110 (lower ankle, longer shin)
'   - THIGH_TILT: new = 6     (degrees, for future bent-thigh implementation)
'   Resulting upper arm ~= 53mm, forearm ~= 54mm, thigh = 55mm, shin = 55mm.
'
' Tier C DOF changes:
'   + Shoulder roll: 2 new axes (AX_L_SHOULDER_ROLL, AX_R_SHOULDER_ROLL).
'     Each shoulder gets a 2nd servo for sideways arm motion.
'   - Waist roll: dropped. PL_WAIST_ROLL removed, AX_WAIST_ROLL removed.
'     Spine now has Z-axis rotation only (waist yaw).
'   Net DOF: 18 (v16) - 1 (waist roll) + 2 (shoulder roll) = 19 (v17).
'
' Axis architecture (13 SW axis features for 19 servos):
'   Shared (one feature, both L and R servos mate to it):
'     AX_HEAD_PAN, AX_WAIST_YAW          (vertical Z at spine)
'     AX_HEAD_TILT, AX_SHOULDER_PITCH,
'     AX_ELBOW_PITCH, AX_HAND_PITCH,
'     AX_HIP_PITCH, AX_KNEE_PITCH,
'     AX_ANKLE_PITCH                     (X-direction at each Z level)
'   L/R specific (different lines per side):
'     AX_L_SHOULDER_ROLL, AX_R_SHOULDER_ROLL  (Y-direction at +/-X)
'     AX_L_HIP_YAW, AX_R_HIP_YAW              (vertical Z at +/-X)
'
' RUN ON A FRESH PART. Idempotency means already-existing planes/axes from
' v16 won't be overwritten - they'll be skipped.
' ============================================================================

Dim swApp As Object
Dim swModel As Object
Dim swModelExt As Object
Dim swFeatMgr As Object
Dim swEqMgr As Object
Dim swSketchMgr As Object

' Per-run counters
Dim varOK As Long, varSkip As Long, varFail As Long
Dim planeOK As Long, planeSkip As Long, planeFail As Long
Dim axisOK As Long, axisSkip As Long, axisFail As Long
Dim sketchOK As Boolean

' Reference plane constraint values (verified from SW2025 macro recorder)
Const REFPLANE_DISTANCE         As Long = 8
Const REFPLANE_DISTANCE_REVERSE As Long = 264

Sub main()
    Set swApp = Application.SldWorks
    Set swModel = swApp.ActiveDoc

    If swModel Is Nothing Then
        MsgBox "Please open or create a new Part first.", vbExclamation
        Exit Sub
    End If

    Dim myModelView As Object
    Set myModelView = swModel.ActiveView
    If Not myModelView Is Nothing Then
        On Error Resume Next
        myModelView.FrameState = 1
        On Error GoTo 0
    End If

    Set swModelExt = swModel.Extension
    Set swFeatMgr = swModel.FeatureManager
    Set swSketchMgr = swModel.SketchManager
    Set swEqMgr = swModel.GetEquationMgr

    If swEqMgr Is Nothing Then
        MsgBox "EquationMgr unavailable. Make sure the active document is a Part.", vbExclamation
        Exit Sub
    End If

    varOK = 0:   varSkip = 0:   varFail = 0
    planeOK = 0: planeSkip = 0: planeFail = 0
    axisOK = 0:  axisSkip = 0:  axisFail = 0
    sketchOK = False

    Debug.Print "=== HawaBot SSP v17 run starting ==="

    Call AddGlobalVariables
    Call CreateReferencePlanes
    Call CreateReferenceAxes
    Call CreateLayoutSketch

    swModel.ForceRebuild3 True

    Dim sketchTxt As String
    If sketchOK Then sketchTxt = "created" Else sketchTxt = "NOT created"

    Debug.Print "=== HawaBot SSP v17 run complete ==="

    MsgBox "HawaBot SSP build report (v17)" & vbCrLf & vbCrLf & _
           "Variables:  " & varOK & " added, " & varSkip & " already existed, " & varFail & " failed" & vbCrLf & _
           "Planes:     " & planeOK & " added, " & planeSkip & " already existed, " & planeFail & " failed" & vbCrLf & _
           "Axes:       " & axisOK & " added, " & axisSkip & " already existed, " & axisFail & " failed" & vbCrLf & _
           "Sketch:     " & sketchTxt & vbCrLf & vbCrLf & _
           "DOF total: 19 (head 2, waist 1, shoulders 4, elbows 2," & vbCrLf & _
           "  hands 2, hips 4, knees 2, ankles 2)" & vbCrLf & vbCrLf & _
           "Open the Immediate Window (Ctrl+G) for per-feature detail.", _
           vbInformation, "HawaBot SSP Builder v17"
End Sub


' ============================================================================
' GENERIC FEATURE-TREE WALKER
' ============================================================================
Function FindFeature(featName As String) As Object
    Set FindFeature = Nothing
    If swModel Is Nothing Then Exit Function

    Dim swFeat As Object
    Set swFeat = swModel.FirstFeature

    Do While Not swFeat Is Nothing
        If StrComp(swFeat.Name, featName, vbTextCompare) = 0 Then
            Set FindFeature = swFeat
            Exit Function
        End If
        Set swFeat = swFeat.GetNextFeature
    Loop
End Function


' ============================================================================
' STEP 1: GLOBAL VARIABLES
' ============================================================================
Sub AddGlobalVariables()

    ' --- Skeleton dimensions ---
    AddVar "TOTAL_H", 250
    AddVar "BASE_W", 100
    AddVar "BASE_D", 80
    AddVar "BASE_H", 25
    AddVar "BASE_R", 8
    AddVar "TORSO_D", 28

    ' --- Joint positions (v17 updated values) ---
    AddVar "WAIST_YAW_Z", 15
    ' WAIST_ROLL_Z dropped (waist roll DOF removed)
    AddVar "SHOULDER_Z", 140
    AddVar "SHOULDER_X", 40                 ' was 48 (narrower shoulder)
    AddVar "ELBOW_Z", 100                   ' was 105 (drops elbow slightly)
    AddVar "ELBOW_X", 75                    ' was 65 (longer reach outward)
    AddVar "HAND_Z", 50                     ' was 70 (longer forearm, Poppy ratio)
    AddVar "HAND_X", 55                     ' new (hand inward of elbow)
    AddVar "HEAD_PAN_Z", 155
    AddVar "HEAD_TILT_Z", 185
    AddVar "HIP_Z", 0
    AddVar "HIP_X", 20
    AddVar "KNEE_Z", -55                    ' was -60 (slightly higher knee)
    AddVar "ANKLE_Z", -110                  ' was -105 (lower ankle, longer shin)
    AddVar "FOOT_L", 40
    AddVar "FOOT_W", 25
    AddVar "FOOT_H", 5
    AddVar "THIGH_TILT_DEG", 6              ' new (Poppy bent-thigh, future use)

    ' --- Clearances ---
    AddVar "C_wall", 0.3
    AddVar "C_wall_dyn", 0.5
    AddVar "T_wall", 2.5
    AddVar "D_wire_main", 8
    AddVar "D_wire_branch", 6
    AddVar "D_wire_small", 4
    AddVar "D_screw", 2

    ' --- SG90 ---
    AddVar "SG90_L", 22.7
    AddVar "SG90_W", 12.2
    AddVar "SG90_H", 22.7
    AddVar "SG90_H_total", 32.3
    AddVar "SG90_tab_L", 32.3
    AddVar "SG90_tab_T", 2.8
    AddVar "SG90_tab_Z", 17
    AddVar "SG90_spline_OD", 4.8
    AddVar "SG90_turret_D", 11.8
    AddVar "SG90_turret_H", 5.96
    AddVar "SG90_hole_D", 2
    AddVar "SG90_hole_inset", 2
    AddVar "SG90_shaft_offset", 6.2

    ' --- MG90S ---
    AddVar "MG90S_L", 22.8
    AddVar "MG90S_W", 12.4
    AddVar "MG90S_H", 22.5
    AddVar "MG90S_H_total", 32.5
    AddVar "MG90S_tab_L", 32.1
    AddVar "MG90S_tab_T", 2.8
    AddVar "MG90S_tab_Z", 18.5
    AddVar "MG90S_spline_OD", 4.8
    AddVar "MG90S_hole_D", 2

    ' --- XL330 ---
    AddVar "XL330_W", 20
    AddVar "XL330_H", 34
    AddVar "XL330_D", 26
    AddVar "XL330_mount_spacing_x", 8
    AddVar "XL330_mount_spacing_z", 16
    AddVar "XL330_mount_hole_D", 2
    AddVar "XL330_horn_D", 30

    ' --- Pi 5 ---
    AddVar "PI5_L", 85
    AddVar "PI5_W", 56
    AddVar "PI5_H", 21
    AddVar "PI5_hole_spacing_L", 58
    AddVar "PI5_hole_spacing_W", 49
    AddVar "PI5_hole_D", 2.7
    AddVar "PI5_hole_edge", 3.5

    ' --- PCA9685 ---
    AddVar "PCA9685_L", 62.5
    AddVar "PCA9685_W", 25.4
    AddVar "PCA9685_hole_spacing_L", 55.9
    AddVar "PCA9685_hole_spacing_W", 19.1

    ' --- Audio ---
    AddVar "SPEAKER_D", 28
    AddVar "SPEAKER_H", 12
    AddVar "SPEAKER_PORT_D", 25
    AddVar "AMP_L", 19.4
    AddVar "AMP_W", 17.8
    AddVar "AMP_H", 3
    AddVar "MIC_L", 14
    AddVar "MIC_W", 14
    AddVar "MIC_H", 3
    AddVar "MIC_HOLE_D", 1.5

    ' --- Sensors ---
    AddVar "IMU_L", 21
    AddVar "IMU_W", 16
    AddVar "IMU_H", 3.8
    AddVar "ULTRASONIC_L", 40
    AddVar "ULTRASONIC_W", 18
    AddVar "ULTRASONIC_H", 15.6
    AddVar "ULTRASONIC_EYE_D", 10
    AddVar "ULTRASONIC_EYE_SPACING", 16
    AddVar "LED_SIZE", 5

    ' --- Power ---
    AddVar "BATTERY_L", 40
    AddVar "BATTERY_W", 30
    AddVar "BATTERY_H", 8
    AddVar "TP4056_L", 25
    AddVar "TP4056_W", 17
    AddVar "TP4056_H", 4

    ' --- Magnets ---
    AddVar "MAG_D", 6
    AddVar "MAG_H", 3
    AddVar "MAG_POCKET_D", 6.1
    AddVar "MAG_POCKET_H", 3.1

End Sub

Sub AddVar(varName As String, value As Double)
    Dim eq As String
    eq = """" & varName & """= " & CStr(value)

    Dim result As Long
    result = swEqMgr.Add2(-1, eq, True)

    If result < 0 Then
        varSkip = varSkip + 1
    Else
        varOK = varOK + 1
    End If
End Sub


' ============================================================================
' STEP 2: REFERENCE PLANES (21 planes total)
' ============================================================================
Sub CreateReferencePlanes()
    ' --- Horizontal planes (offset from Top Plane along Z) ---
    ' Above origin
    MakeOffsetPlaneDir "PL_WAIST_YAW",  "Top Plane", 15,    False
    MakeOffsetPlaneDir "PL_SHOULDER",   "Top Plane", 140,   False
    MakeOffsetPlaneDir "PL_ELBOW_Z",    "Top Plane", 100,   False    ' NEW
    MakeOffsetPlaneDir "PL_HAND_Z",     "Top Plane", 50,    False    ' NEW
    MakeOffsetPlaneDir "PL_HEAD_PAN",   "Top Plane", 155,   False
    MakeOffsetPlaneDir "PL_HEAD_TILT",  "Top Plane", 185,   False

    ' At origin (tiny positive offset)
    MakeOffsetPlaneDir "PL_HIP",        "Top Plane", 0.001, False

    ' Below origin (constraint=264 reverse)
    MakeOffsetPlaneDir "PL_KNEE",       "Top Plane", 55,    True     ' was 60
    MakeOffsetPlaneDir "PL_ANKLE",      "Top Plane", 110,   True     ' was 105

    ' --- Vertical planes (offset from Right Plane along X) ---
    ' Right side: positive offset (constraint=8)
    MakeOffsetPlaneDir "PL_R_SHOULDER", "Right Plane", 40,  False    ' was 48
    MakeOffsetPlaneDir "PL_R_ELBOW",    "Right Plane", 75,  False    ' was 65
    MakeOffsetPlaneDir "PL_R_HAND",     "Right Plane", 55,  False    ' was 65
    MakeOffsetPlaneDir "PL_R_HIP",      "Right Plane", 20,  False
    MakeOffsetPlaneDir "PL_R_KNEE_X",   "Right Plane", 20,  False
    MakeOffsetPlaneDir "PL_R_ANKLE_X",  "Right Plane", 20,  False

    ' Left side: reverse direction (constraint=264)
    MakeOffsetPlaneDir "PL_L_SHOULDER", "Right Plane", 40,  True     ' was 48
    MakeOffsetPlaneDir "PL_L_ELBOW",    "Right Plane", 75,  True     ' was 65
    MakeOffsetPlaneDir "PL_L_HAND",     "Right Plane", 55,  True     ' was 65
    MakeOffsetPlaneDir "PL_L_HIP",      "Right Plane", 20,  True
    MakeOffsetPlaneDir "PL_L_KNEE_X",   "Right Plane", 20,  True
    MakeOffsetPlaneDir "PL_L_ANKLE_X",  "Right Plane", 20,  True
End Sub

Sub MakeOffsetPlaneDir(planeName As String, refPlaneName As String, _
                       distanceMM As Double, reverseDir As Boolean)
    If Not FindFeature(planeName) Is Nothing Then
        planeSkip = planeSkip + 1
        Exit Sub
    End If

    Dim swRefFeat As Object
    Set swRefFeat = FindFeature(refPlaneName)
    If swRefFeat Is Nothing Then
        Debug.Print "FAIL plane " & planeName & ": reference not found: " & refPlaneName
        planeFail = planeFail + 1
        Exit Sub
    End If

    swModel.ClearSelection2 True

    Dim selOK As Boolean
    selOK = swRefFeat.Select2(False, 0)
    If Not selOK Then
        Debug.Print "FAIL plane " & planeName & ": Select2 returned False on " & refPlaneName
        planeFail = planeFail + 1
        Exit Sub
    End If

    Dim constraint As Long
    If reverseDir Then
        constraint = REFPLANE_DISTANCE_REVERSE
    Else
        constraint = REFPLANE_DISTANCE
    End If

    Dim distM As Double
    distM = distanceMM / 1000#

    Dim swRefPlane As Object
    Set swRefPlane = swFeatMgr.InsertRefPlane(constraint, distM, 0, 0, 0, 0)

    If Not swRefPlane Is Nothing Then
        swRefPlane.Name = planeName
        planeOK = planeOK + 1

        Dim sign As String
        If reverseDir Then sign = "-" Else sign = "+"
        Debug.Print "OK plane " & planeName & "  ref=" & refPlaneName & _
                    "  offset=" & sign & distanceMM & "mm"
    Else
        Debug.Print "FAIL plane " & planeName & ": InsertRefPlane returned Nothing"
        planeFail = planeFail + 1
    End If

    swModel.ClearSelection2 True
End Sub


' ============================================================================
' STEP 3: REFERENCE AXES (13 axis features for 19 servos)
'
' Naming convention (more explicit than v16):
'   *_PITCH = rotation about X axis (forward/back swing)   -> X-direction line
'   *_ROLL  = rotation about Y axis (sideways tilt)        -> Y-direction line
'   *_YAW   = rotation about Z axis (twist)                -> Z-direction line
'
' Two-plane intersection rules:
'   horizontal plane n vertical plane = horizontal line
'   two vertical planes              = vertical line
'   So YAW axes need TWO vertical planes intersecting at the joint.
' ============================================================================
Sub CreateReferenceAxes()
    ' === HEAD ===
    ' Head pan = vertical Z axis at spine center
    MakeAxisFrom2Planes "AX_HEAD_PAN",  "Right Plane", "Front Plane"
    ' Head tilt = X-direction line at head tilt height
    MakeAxisFrom2Planes "AX_HEAD_TILT", "PL_HEAD_TILT", "Front Plane"

    ' === SPINE (only Z-axis rotation per Tier C option B) ===
    ' Waist yaw = vertical Z axis at spine center (same line as AX_HEAD_PAN)
    MakeAxisFrom2Planes "AX_WAIST_YAW", "Right Plane", "Front Plane"

    ' === SHOULDER (pitch + roll, both L and R servos use these) ===
    ' Shoulder pitch = X-direction line at shoulder height (shared L/R)
    MakeAxisFrom2Planes "AX_SHOULDER_PITCH", "PL_SHOULDER", "Front Plane"
    ' Shoulder roll = Y-direction line at each shoulder X (separate L/R)
    MakeAxisFrom2Planes "AX_L_SHOULDER_ROLL", "PL_L_SHOULDER", "PL_SHOULDER"
    MakeAxisFrom2Planes "AX_R_SHOULDER_ROLL", "PL_R_SHOULDER", "PL_SHOULDER"

    ' === ELBOW (pitch only, shared L/R) ===
    MakeAxisFrom2Planes "AX_ELBOW_PITCH", "PL_ELBOW_Z", "Front Plane"

    ' === HAND (pitch only, shared L/R) ===
    MakeAxisFrom2Planes "AX_HAND_PITCH", "PL_HAND_Z", "Front Plane"

    ' === HIP (yaw separate L/R, pitch shared) ===
    ' Hip yaw = vertical Z line at each hip
    MakeAxisFrom2Planes "AX_L_HIP_YAW", "PL_L_HIP", "Front Plane"
    MakeAxisFrom2Planes "AX_R_HIP_YAW", "PL_R_HIP", "Front Plane"
    ' Hip pitch = X-direction line at hip level (shared L/R)
    MakeAxisFrom2Planes "AX_HIP_PITCH", "PL_HIP", "Front Plane"

    ' === KNEE (pitch only, shared L/R) ===
    MakeAxisFrom2Planes "AX_KNEE_PITCH", "PL_KNEE", "Front Plane"

    ' === ANKLE (pitch only, shared L/R) ===
    MakeAxisFrom2Planes "AX_ANKLE_PITCH", "PL_ANKLE", "Front Plane"
End Sub

Sub MakeAxisFrom2Planes(axisName As String, plane1 As String, plane2 As String)
    If Not FindFeature(axisName) Is Nothing Then
        axisSkip = axisSkip + 1
        Exit Sub
    End If

    Dim swFeat1 As Object
    Dim swFeat2 As Object
    Set swFeat1 = FindFeature(plane1)
    Set swFeat2 = FindFeature(plane2)

    If swFeat1 Is Nothing Then
        Debug.Print "FAIL axis " & axisName & ": plane1 not in tree: " & plane1
        axisFail = axisFail + 1
        Exit Sub
    End If
    If swFeat2 Is Nothing Then
        Debug.Print "FAIL axis " & axisName & ": plane2 not in tree: " & plane2
        axisFail = axisFail + 1
        Exit Sub
    End If

    swModel.ClearSelection2 True

    Dim sel1 As Boolean, sel2 As Boolean
    sel1 = swModelExt.SelectByID2(plane1, "PLANE", 0, 0, 0, False, 0, Nothing, 0)
    sel2 = swModelExt.SelectByID2(plane2, "PLANE", 0, 0, 0, True, 0, Nothing, 0)

    If Not sel1 Then sel1 = swFeat1.Select2(False, 0)
    If Not sel2 Then sel2 = swFeat2.Select2(True, 0)

    If Not sel1 Or Not sel2 Then
        Debug.Print "FAIL axis " & axisName & ": selection failed"
        axisFail = axisFail + 1
        swModel.ClearSelection2 True
        Exit Sub
    End If

    Dim ok As Boolean
    ok = swModel.InsertAxis2(True)

    If Not ok Then
        Debug.Print "FAIL axis " & axisName & ": swModel.InsertAxis2 returned False"
        axisFail = axisFail + 1
        swModel.ClearSelection2 True
        Exit Sub
    End If

    Dim swFeat As Object
    Set swFeat = swModelExt.GetLastFeatureAdded

    If Not swFeat Is Nothing Then
        swFeat.Name = axisName
        axisOK = axisOK + 1
        Debug.Print "OK axis " & axisName & "  = " & plane1 & " n " & plane2
    Else
        Debug.Print "FAIL axis " & axisName & ": GetLastFeatureAdded returned Nothing"
        axisFail = axisFail + 1
    End If

    swModel.ClearSelection2 True
End Sub


' ============================================================================
' STEP 4: LAYOUT SKETCH
'   Updated to reflect new arm/leg proportions.
' ============================================================================
Sub CreateLayoutSketch()
    If Not FindFeature("KINEMATIC_LAYOUT") Is Nothing Then
        sketchOK = True
        Exit Sub
    End If

    swSketchMgr.Insert3DSketch True
    swSketchMgr.AddToDB = True

    ' --- SPINE ---
    CLine 0, 0, -0.025, 0, 0, 0              ' Base bottom to ground
    CLine 0, 0, 0, 0, 0, 0.015                ' Ground to waist yaw
    CLine 0, 0, 0.015, 0, 0, 0.14             ' Waist yaw to shoulders (no waist roll now)
    CLine 0, 0, 0.14, 0, 0, 0.155             ' Shoulders to head pan
    CLine 0, 0, 0.155, 0, 0, 0.185            ' Head pan to head tilt
    CLine 0, 0, 0.185, 0, 0, 0.21             ' Head tilt to top of head

    ' --- LEFT ARM (new proportions: shoulder X=-40, elbow X=-75 Z=100, hand X=-55 Z=50) ---
    CLine 0, 0, 0.14, -0.04, 0, 0.14          ' Spine to L shoulder
    CLine -0.04, 0, 0.14, -0.075, 0, 0.1      ' L shoulder to elbow
    CLine -0.075, 0, 0.1, -0.055, 0, 0.05     ' L elbow to hand

    ' --- RIGHT ARM ---
    CLine 0, 0, 0.14, 0.04, 0, 0.14
    CLine 0.04, 0, 0.14, 0.075, 0, 0.1
    CLine 0.075, 0, 0.1, 0.055, 0, 0.05

    ' --- LEFT LEG (knee Z=-55, ankle Z=-110) ---
    CLine 0, 0, 0, -0.02, 0, 0                ' Hip
    CLine -0.02, 0, 0, -0.02, 0, -0.055       ' Hip to knee
    CLine -0.02, 0, -0.055, -0.02, 0, -0.11   ' Knee to ankle
    CLine -0.02, 0, -0.11, -0.02, 0, -0.115   ' Ankle to foot top
    CLine -0.04, 0, -0.115, 0, 0, -0.115      ' L foot plate

    ' --- RIGHT LEG ---
    CLine 0, 0, 0, 0.02, 0, 0
    CLine 0.02, 0, 0, 0.02, 0, -0.055
    CLine 0.02, 0, -0.055, 0.02, 0, -0.11
    CLine 0.02, 0, -0.11, 0.02, 0, -0.115
    CLine 0, 0, -0.115, 0.04, 0, -0.115

    ' --- BASE PLATE OUTLINE ---
    CLine -0.05, -0.04, -0.025, 0.05, -0.04, -0.025
    CLine 0.05, -0.04, -0.025, 0.05, 0.04, -0.025
    CLine 0.05, 0.04, -0.025, -0.05, 0.04, -0.025
    CLine -0.05, 0.04, -0.025, -0.05, -0.04, -0.025

    swSketchMgr.AddToDB = False
    swSketchMgr.Insert3DSketch True

    Dim swFeat As Object
    Set swFeat = swModelExt.GetLastFeatureAdded
    If Not swFeat Is Nothing Then
        swFeat.Name = "KINEMATIC_LAYOUT"
        sketchOK = True
    End If
End Sub

Sub CLine(x1 As Double, y1 As Double, z1 As Double, _
          x2 As Double, y2 As Double, z2 As Double)
    Dim seg As Object
    Set seg = swSketchMgr.CreateLine(x1, y1, z1, x2, y2, z2)
    If Not seg Is Nothing Then
        seg.ConstructionGeometry = True
    End If
End Sub
