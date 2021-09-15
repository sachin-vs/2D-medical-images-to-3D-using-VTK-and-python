#!/usr/bin/env python

import vtk


def main():
    # vtkFlyingEdges3D was introduced in VTK >= 8.2
    use_flying_edges = vtk_version_ok(8, 2, 0)

    colors = vtk.vtkNamedColors()

    dicom_dir= 'ct' 
    iso_value = 1800 #get_program_parameters()
    if iso_value is None and dicom_dir is not None:
        print('An ISO value is needed.')
        return ()

    volume = vtk.vtkImageData()
    if dicom_dir is None:
        sphere_source = vtk.vtkSphereSource()
        sphere_source.SetPhiResolution(20)
        sphere_source.SetThetaResolution(20)
        sphere_source.Update()

        bounds = list(sphere_source.GetOutput().GetBounds())
        for i in range(0, 6, 2):
            dist = bounds[i + 1] - bounds[i]
            bounds[i] = bounds[i] - 0.1 * dist
            bounds[i + 1] = bounds[i + 1] + 0.1 * dist
        voxel_modeller = vtk.vtkVoxelModeller()
        voxel_modeller.SetSampleDimensions(50, 50, 50)
        voxel_modeller.SetModelBounds(bounds)
        voxel_modeller.SetScalarTypeToFloat()
        voxel_modeller.SetMaximumDistance(0.1)

        voxel_modeller.SetInputConnection(sphere_source.GetOutputPort())
        voxel_modeller.Update()
        iso_value = 0.5
        volume.DeepCopy(voxel_modeller.GetOutput())
    else:
        reader = vtk.vtkDICOMImageReader()
        reader.SetDirectoryName(dicom_dir)
        reader.Update()
        volume.DeepCopy(reader.GetOutput())

    if use_flying_edges:
        try:
            surface = vtk.vtkFlyingEdges3D()
        except AttributeError:
            surface = vtk.vtkMarchingCubes()
    else:
        surface = vtk.vtkMarchingCubes()
    surface.SetInputData(volume)
    surface.ComputeNormalsOn()
    surface.SetValue(0, iso_value)

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(colors.GetColor3d('DarkSlateGray'))

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetWindowName('MarchingCubes')

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(surface.GetOutputPort())
    mapper.ScalarVisibilityOff()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d('MistyRose'))

    renderer.AddActor(actor)

    render_window.Render()
    interactor.Start()


def get_program_parameters():
    import argparse
    description = 'The skin extracted from a CT dataset of the head.'
    epilogue = '''
    Derived from VTK/Examples/Cxx/Medical1.cxx
    This example reads a volume dataset, extracts an isosurface that
     represents the skin and displays it.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-d', default=None, help='A DICOM Image directory.')
    parser.add_argument('-i', type=float, default=None, help='The iso value to use.')
    args = parser.parse_args()
    return args.d, args.i


def vtk_version_ok(major, minor, build):
    """
    Check the VTK version.

    :param major: Major version.
    :param minor: Minor version.
    :param build: Build version.
    :return: True if the requested VTK version is greater or equal to the actual VTK version.
    """
    needed_version = 10000000000 * int(major) + 100000000 * int(minor) + int(build)
    try:
        vtk_version_number = vtk.VTK_VERSION_NUMBER
    except AttributeError:  # as error:
        ver = vtk.vtkVersion()
        vtk_version_number = 10000000000 * ver.GetVTKMajorVersion() + 100000000 * ver.GetVTKMinorVersion() \
                             + ver.GetVTKBuildVersion()
    if vtk_version_number >= needed_version:
        return True
    else:
        return False


if __name__ == '__main__':
    main()
