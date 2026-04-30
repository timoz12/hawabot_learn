Attribute VB_Name = "HawaBotSSP"
' ============================================================================
' HawaBot Pro — Skeleton Sketch Part (SSP) Builder Macro
' SolidWorks 2025
'
' Creates the complete kinematic skeleton in the active part:
'   1. All global variables (70+ joint positions, component dimensions)
'   2. Reference planes at every joint (18 planes)
'   3. Reference axes for every rotation (18 axes)
'   4. 3D layout sketch with construction lines (kinematic chain)
'
' HOW TO USE:
'   Option A (recommended):
'     1. Open SolidWorks -> File -> New -> Part (mmgs template)
'     2. Save as "hawabot_skeleton_sketch.sldprt"
'     3. Tools -> Macro -> New -> save as "hawabot_ssp.swp"
'     4. In the VBA editor: File -> Import File -> select this .bas file
'     5. Delete the empty "Module1" that was auto-created
'     6. Run (F5) or close editor and run via Tools -> Macro -> Run
'
'   Option B:
'     1. Open SolidWorks -> File -> New -> Part
'     2. Tools -> Macro -> Run -> change file type to "Basic Files (*.bas)"
'     3. Select this file -> Run
'
' ============================================================================

Dim swApp As SldWorks.SldWorks
Dim swModel As SldWorks.ModelDoc2
Dim swModelExt As SldWorks.ModelDocExtension
Dim swFeatMgr As SldWorks.FeatureManager
Dim swEqMgr As SldWorks.EquationMgr
Dim swSketchMgr As SldWorks.SketchManager

Sub main()
    Set swApp = Application.SldWorks
    Set swModel = swApp.ActiveDoc

    If swModel Is Nothing Then
        MsgBox "Please open or create a new Part first.", vbExclamation
        Exit Sub
    End If

    Set swModelExt = swModel.Extension
    Set swFeatMgr = swModel.FeatureManager
    Set swSketchMgr = swModel.SketchManager
    Set swEqMgr = swModel.GetEquationMgr

    ' Step 1: Add all global variables
    Call AddGlobalVariables

    ' Step 2: Create reference planes at each joint
    Call CreateReferencePlanes

    ' Step 3: Create reference axes at each joint
    Call CreateReferenceAxes

    ' Step 4: Create layout sketch with kinematic chain
    Call CreateLayoutSketch

    ' Rebuild to apply everything
    swModel.ForceRebuild3 True

    MsgBox "HawaBot SSP created successfully!" & vbCrLf & vbCrLf & _
           "Created:" & vbCrLf & _
           "  - 70+ global variables" & vbCrLf & _
           "  - 18 reference planes" & vbCrLf & _
           "  - 18 reference axes" & vbCrLf & _
           "  - Kinematic layout sketch" & vbCrLf & vbCrLf & _
           "Next: Create the master assembly and place components.", _
           vbInformation, "HawaBot SSP Builder"
End Sub


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

    ' --- Joint positions (Z = vertical, X = lateral) ---
    AddVar "WAIST_YAW_Z", 15
    AddVar "WAIST_ROLL_Z", 45
    AddVar "SHOULDER_Z", 140
    AddVar "SHOULDER_X", 48
    AddVar "ELBOW_Z", 105
    AddVar "ELBOW_X", 65
    AddVar "HAND_Z", 70
    AddVar "HEAD_PAN_Z", 155
    AddVar "HEAD_TILT_Z", 185
    AddVar "HIP_Z", 0
    AddVar "HIP_X", 20
    AddVar "KNEE_Z", -60
    AddVar "ANKLE_Z", -105
    AddVar "FOOT_L", 40
    AddVar "FOOT_W", 25
    AddVar "FOOT_H", 5

    ' --- Clearances ---
    AddVar "C_wall", 0.3
    AddVar "C_wall_dyn", 0.5
    AddVar "T_wall", 2.5
    AddVar "D_wire_main", 8
    AddVar "D_wire_branch", 6
    AddVar "D_wire_small", 4
    AddVar "D_screw", 2

    ' --- SG90 Micro Servo ---
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

    ' --- MG90S Metal Gear Servo ---
    AddVar "MG90S_L", 22.8
    AddVar "MG90S_W", 12.4
    AddVar "MG90S_H", 22.5
    AddVar "MG90S_H_total", 32.5
    AddVar "MG90S_tab_L", 32.1
    AddVar "MG90S_tab_T", 2.8
    AddVar "MG90S_tab_Z", 18.5
    AddVar "MG90S_spline_OD", 4.8
    AddVar "MG90S_hole_D", 2

    ' --- Dynamixel XL330 ---
    AddVar "XL330_W", 20
    AddVar "XL330_H", 34
    AddVar "XL330_D", 26
    AddVar "XL330_mount_spacing_x", 8
    AddVar "XL330_mount_spacing_z", 16
    AddVar "XL330_mount_hole_D", 2
    AddVar "XL330_horn_D", 30

    ' --- Raspberry Pi 5 ---
    AddVar "PI5_L", 85
    AddVar "PI5_W", 56
    AddVar "PI5_H", 21
    AddVar "PI5_hole_spacing_L", 58
    AddVar "PI5_hole_spacing_W", 49
    AddVar "PI5_hole_D", 2.7
    AddVar "PI5_hole_edge", 3.5

    ' --- PCA9685 Servo Driver ---
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
    result = swEqMgr.Add2(0, eq, True)

    ' If Add2 returns non-zero, try with index -1
    If result <> 0 Then
        result = swEqMgr.Add2(-1, eq, True)
    End If

    If result <> 0 Then
        Debug.Print "Warning: Could not add variable: " & varName
    End If
End Sub


' ============================================================================
' STEP 2: REFERENCE PLANES
' ============================================================================
Sub CreateReferencePlanes()
    ' Horizontal planes (offset from Top Plane along Z)
    MakeOffsetPlane "PL_WAIST_YAW", "Top Plane", 15
    MakeOffsetPlane "PL_WAIST_ROLL", "Top Plane", 45
    MakeOffsetPlane "PL_SHOULDER", "Top Plane", 140
    MakeOffsetPlane "PL_HEAD_PAN", "Top Plane", 155
    MakeOffsetPlane "PL_HEAD_TILT", "Top Plane", 185
    MakeOffsetPlane "PL_HIP", "Top Plane", 0.001       ' Tiny offset — can't be exactly 0
    MakeOffsetPlane "PL_KNEE", "Top Plane", 60          ' |Z|=60, flipped
    MakeOffsetPlane "PL_ANKLE", "Top Plane", 105        ' |Z|=105, flipped

    ' Vertical planes (offset from Right Plane along X)
    MakeOffsetPlane "PL_L_SHOULDER", "Right Plane", 48
    MakeOffsetPlane "PL_R_SHOULDER", "Right Plane", 48  ' Same offset, opposite side done via flip
    MakeOffsetPlane "PL_L_ELBOW", "Right Plane", 65
    MakeOffsetPlane "PL_R_ELBOW", "Right Plane", 65
    MakeOffsetPlane "PL_L_HAND", "Right Plane", 65
    MakeOffsetPlane "PL_R_HAND", "Right Plane", 65
    MakeOffsetPlane "PL_L_HIP", "Right Plane", 20
    MakeOffsetPlane "PL_R_HIP", "Right Plane", 20
    MakeOffsetPlane "PL_L_KNEE_X", "Right Plane", 20
    MakeOffsetPlane "PL_R_KNEE_X", "Right Plane", 20
    MakeOffsetPlane "PL_L_ANKLE_X", "Right Plane", 20
    MakeOffsetPlane "PL_R_ANKLE_X", "Right Plane", 20
End Sub

Sub MakeOffsetPlane(planeName As String, refPlaneName As String, offsetMM As Double)
    swModel.ClearSelection2 True

    Dim boolstatus As Boolean
    boolstatus = swModel.Extension.SelectByID2(refPlaneName, "PLANE", 0, 0, 0, False, 0, Nothing, 0)
    If Not boolstatus Then
        Debug.Print "Could not select: " & refPlaneName
        Exit Sub
    End If

    ' API expects meters
    Dim offsetM As Double
    offsetM = offsetMM / 1000#

    Dim swRefPlane As SldWorks.Feature
    Set swRefPlane = swFeatMgr.InsertRefPlane(8, offsetM, 0, 0, 0, 0)
    '  8 = swRefPlaneReferenceConstraint_Distance (parallel at distance)

    If Not swRefPlane Is Nothing Then
        swRefPlane.name = planeName
    Else
        Debug.Print "Failed to create plane: " & planeName
    End If

    swModel.ClearSelection2 True
End Sub


' ============================================================================
' STEP 3: REFERENCE AXES
' ============================================================================
Sub CreateReferenceAxes()
    ' Z-axis rotations (yaw) — intersection of horizontal plane + Front Plane
    MakeAxisFrom2Planes "AX_WAIST_YAW", "PL_WAIST_YAW", "Front Plane"
    MakeAxisFrom2Planes "AX_HEAD_PAN", "PL_HEAD_PAN", "Front Plane"
    MakeAxisFrom2Planes "AX_L_HIP_YAW", "PL_HIP", "PL_L_HIP"
    MakeAxisFrom2Planes "AX_R_HIP_YAW", "PL_HIP", "PL_R_HIP"

    ' Y-axis rotations (roll/tilt) — intersection of horizontal plane + Right Plane
    MakeAxisFrom2Planes "AX_WAIST_ROLL", "PL_WAIST_ROLL", "Right Plane"
    MakeAxisFrom2Planes "AX_HEAD_TILT", "PL_HEAD_TILT", "Right Plane"

    ' X-axis rotations (pitch) — intersection of vertical + horizontal planes
    MakeAxisFrom2Planes "AX_L_SHOULDER", "PL_L_SHOULDER", "PL_SHOULDER"
    MakeAxisFrom2Planes "AX_R_SHOULDER", "PL_R_SHOULDER", "PL_SHOULDER"
    MakeAxisFrom2Planes "AX_L_ELBOW", "PL_L_ELBOW", "PL_SHOULDER"
    MakeAxisFrom2Planes "AX_R_ELBOW", "PL_R_ELBOW", "PL_SHOULDER"
    MakeAxisFrom2Planes "AX_L_HAND", "PL_L_HAND", "PL_SHOULDER"
    MakeAxisFrom2Planes "AX_R_HAND", "PL_R_HAND", "PL_SHOULDER"
    MakeAxisFrom2Planes "AX_L_HIP_PITCH", "PL_L_HIP", "PL_HIP"
    MakeAxisFrom2Planes "AX_R_HIP_PITCH", "PL_R_HIP", "PL_HIP"
    MakeAxisFrom2Planes "AX_L_KNEE", "PL_L_KNEE_X", "PL_KNEE"
    MakeAxisFrom2Planes "AX_R_KNEE", "PL_R_KNEE_X", "PL_KNEE"
    MakeAxisFrom2Planes "AX_L_ANKLE", "PL_L_ANKLE_X", "PL_ANKLE"
    MakeAxisFrom2Planes "AX_R_ANKLE", "PL_R_ANKLE_X", "PL_ANKLE"
End Sub

Sub MakeAxisFrom2Planes(axisName As String, plane1 As String, plane2 As String)
    swModel.ClearSelection2 True

    Dim b1 As Boolean, b2 As Boolean
    b1 = swModel.Extension.SelectByID2(plane1, "PLANE", 0, 0, 0, False, 0, Nothing, 0)
    b2 = swModel.Extension.SelectByID2(plane2, "PLANE", 0, 0, 0, True, 0, Nothing, 0)

    If Not b1 Or Not b2 Then
        Debug.Print "Could not select planes for axis: " & axisName
        Exit Sub
    End If

    Dim swFeat As SldWorks.Feature
    Set swFeat = swFeatMgr.InsertAxis2(True)

    If Not swFeat Is Nothing Then
        swFeat.name = axisName
    Else
        Debug.Print "Failed to create axis: " & axisName
    End If

    swModel.ClearSelection2 True
End Sub


' ============================================================================
' STEP 4: LAYOUT SKETCH (3D Construction Lines — Kinematic Chain)
' ============================================================================
Sub CreateLayoutSketch()
    swSketchMgr.Insert3DSketch True
    swSketchMgr.AddToDB = True

    ' API uses meters. Helper draws construction lines.

    ' --- SPINE (vertical centerline) ---
    CLine 0, 0, -0.025, 0, 0, 0              ' Base bottom to ground
    CLine 0, 0, 0, 0, 0, 0.015               ' Ground to waist yaw
    CLine 0, 0, 0.015, 0, 0, 0.045            ' Waist yaw to roll
    CLine 0, 0, 0.045, 0, 0, 0.14             ' Waist to shoulders
    CLine 0, 0, 0.14, 0, 0, 0.155             ' Shoulders to head pan
    CLine 0, 0, 0.155, 0, 0, 0.185            ' Head pan to tilt
    CLine 0, 0, 0.185, 0, 0, 0.21             ' Tilt to top of head

    ' --- LEFT ARM ---
    CLine 0, 0, 0.14, -0.048, 0, 0.14         ' Center to L shoulder
    CLine -0.048, 0, 0.14, -0.065, 0, 0.105   ' L shoulder to elbow
    CLine -0.065, 0, 0.105, -0.065, 0, 0.07   ' L elbow to hand

    ' --- RIGHT ARM ---
    CLine 0, 0, 0.14, 0.048, 0, 0.14          ' Center to R shoulder
    CLine 0.048, 0, 0.14, 0.065, 0, 0.105     ' R shoulder to elbow
    CLine 0.065, 0, 0.105, 0.065, 0, 0.07     ' R elbow to hand

    ' --- LEFT LEG ---
    CLine 0, 0, 0, -0.02, 0, 0                ' Center to L hip
    CLine -0.02, 0, 0, -0.02, 0, -0.06        ' L hip to knee
    CLine -0.02, 0, -0.06, -0.02, 0, -0.105   ' L knee to ankle
    CLine -0.02, 0, -0.105, -0.02, 0, -0.115  ' L ankle to foot bottom
    CLine -0.04, 0, -0.115, 0, 0, -0.115      ' L foot plate

    ' --- RIGHT LEG ---
    CLine 0, 0, 0, 0.02, 0, 0                 ' Center to R hip
    CLine 0.02, 0, 0, 0.02, 0, -0.06          ' R hip to knee
    CLine 0.02, 0, -0.06, 0.02, 0, -0.105     ' R knee to ankle
    CLine 0.02, 0, -0.105, 0.02, 0, -0.115    ' R ankle to foot bottom
    CLine 0, 0, -0.115, 0.04, 0, -0.115       ' R foot plate

    ' --- BASE PLATE OUTLINE ---
    CLine -0.05, -0.04, -0.025, 0.05, -0.04, -0.025
    CLine 0.05, -0.04, -0.025, 0.05, 0.04, -0.025
    CLine 0.05, 0.04, -0.025, -0.05, 0.04, -0.025
    CLine -0.05, 0.04, -0.025, -0.05, -0.04, -0.025

    swSketchMgr.AddToDB = False
    swSketchMgr.Insert3DSketch True  ' Close sketch

    ' Rename
    Dim swFeat As SldWorks.Feature
    Set swFeat = swModelExt.GetLastFeatureAdded
    If Not swFeat Is Nothing Then
        swFeat.name = "KINEMATIC_LAYOUT"
    End If
End Sub

Sub CLine(x1 As Double, y1 As Double, z1 As Double, _
          x2 As Double, y2 As Double, z2 As Double)
    Dim seg As SldWorks.SketchSegment
    Set seg = swSketchMgr.CreateLine(x1, y1, z1, x2, y2, z2)
    If Not seg Is Nothing Then
        seg.ConstructionGeometry = True
    End If
End Sub
