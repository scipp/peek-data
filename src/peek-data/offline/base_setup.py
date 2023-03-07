import scipp as sc
import plopp as pp
from ess import amor, reflectometry
import plopp as pp
from orsopy import fileio
from ess.amor.orso import make_orso

pp.patch_scipp()

def get_sample_plot():
    da = pp.data.data1d()
    pp.backends['2d'] = 'plotly'
    fig = pp.plot(da)._fig.canvas.fig
    pp.backends['2d'] = 'matplotlib'
    return fig

sample_rotation = sc.scalar(0.7989, unit='deg')
sample_beamline = amor.make_beamline(sample_rotation=sample_rotation)
reference_rotation = sc.scalar(0.8389, unit='deg')
reference_beamline = amor.make_beamline(sample_rotation=reference_rotation)

owner = fileio.base.Person('Jochen Stahn', 'Paul Scherrer Institut', 'jochen.stahn@psi.ch')
sample = fileio.data_source.Sample('Ni/Ti Multilayer', 'gas/solid', 'air | (Ni | Ti) * 5 | Si')
creator = fileio.base.Person('Andrew R. McCluskey', 'European Spallation Source', 'andrew.mccluskey@ess.eu')

orso = make_orso(owner=owner,
                 sample=sample,
                 creator=creator,
                 reduction_script='https://github.com/scipp/ess/blob/main/docs/instruments/amor/amor_reduction.ipynb')

sample = amor.load(amor.data.get_path("sample.nxs"),
                   orso=orso,
                   beamline=sample_beamline)
reference = amor.load(amor.data.get_path("reference.nxs"),
                      orso=orso,
                      beamline=reference_beamline)

def pixel_position_correction(data: sc.DataArray):
    return data.coords['position'].fields.z * sc.tan(2.0 *
                                                     data.coords['sample_rotation'] -
                                                     (0.955 * sc.units.deg))

sample.coords['position'].fields.y += pixel_position_correction(sample)
reference.coords['position'].fields.y += pixel_position_correction(reference)
sample.attrs['orso'].value.data_source.measurement.comment = 'Pixel positions corrected'
reference.attrs['orso'].value.data_source.measurement.comment = 'Pixel positions corrected'
sample.hist(tof=40).plot().save('assets/sample_raw_2d.png')

plotting_graph = {"plot": lambda sample: sample.hist(tof=40)}


graph = amor.conversions.specular_reflection()
sc.show_graph(graph, simplified=True).render('assets/workflow_graph', format='png')

wavelength_edges = sc.array(dims=['wavelength'],
                            values=[2.4, 16.0],
                            unit='angstrom')
sample_wav = reflectometry.conversions.tof_to_wavelength(sample, wavelength_edges, graph=graph)
# sample_wav.bins.concat('detector_id').hist(wavelength=200).plot()
reference_wav = reflectometry.conversions.tof_to_wavelength(
    reference, wavelength_edges, graph=graph)
sample_theta = reflectometry.conversions.wavelength_to_theta(
    sample_wav, graph=graph)
sample_theta = reflectometry.corrections.footprint_correction(sample_theta)
reference_theta = reflectometry.conversions.wavelength_to_theta(
    reference_wav, graph=graph)
reference_theta = reflectometry.corrections.footprint_correction(reference_theta)
sample_theta.coords['wavelength_resolution'] = amor.resolution.wavelength_resolution(
    chopper_1_position=sample.coords['source_chopper_1'].value['position'],
    chopper_2_position=sample.coords['source_chopper_2'].value['position'],
    pixel_position=sample.coords['position'])
sample_theta.bins.coords['angular_resolution'] = amor.resolution.angular_resolution(
    pixel_position=sample.coords['position'],
    theta=sample_theta.bins.coords['theta'],
    detector_spatial_resolution=sample_theta.coords['detector_spatial_resolution'])
sample_theta.coords['sample_size_resolution'] = amor.resolution.sample_size_resolution(
    pixel_position=sample.coords['position'], sample_size=sample.coords['sample_size'])
q_edges = sc.geomspace(dim='Q', start=0.008, stop=0.075, num=200, unit='1/angstrom')

sample_q = reflectometry.conversions.theta_to_q(
    sample_theta, q_edges=q_edges, graph=graph)
reference_q = reflectometry.conversions.theta_to_q(
    reference_theta, q_edges=q_edges, graph=graph)

# pp.plot({'sample': sample_q.sum('detector_id'),
#          'uncalibrated reference': reference_q.sum('detector_id')},
#         norm="log").save('assets/')
reference_q_summed = reflectometry.conversions.sum_bins(reference_q)
reference_q_summed_cal = amor.calibrations.supermirror_calibration(
    reference_q_summed)
pp.plot({'Uncalibrated': reference_q_summed.sum('detector_id'),
         'Calibrated': reference_q_summed_cal.sum('detector_id')},
        norm='log').save('assets/calibration_result.png')

sample_q_summed = reflectometry.conversions.sum_bins(sample_q)

sample_norm = reflectometry.corrections.normalize_by_counts(sample_q_summed)
reference_norm = reflectometry.corrections.normalize_by_counts(reference_q_summed_cal)

normalized = amor.normalize.normalize_by_supermirror(sample_norm, reference_norm)

normalized.plot(norm='log').save('assets/normalized_2d_scatter.png')
normalized.mean('detector_id').plot(norm='log').save('assets/normalized_mean.png')

normalized.coords['sigma_Q'] = amor.resolution.sigma_Q(
    angular_resolution=normalized.coords['angular_resolution'],
    wavelength_resolution=normalized.coords['wavelength_resolution'],
    sample_size_resolution=normalized.coords['sample_size_resolution'],
    q_bins=normalized.coords['Q'])
sample_theta = sample.transform_coords(["theta", "wavelength"], graph=graph)
sample_theta = sample_theta.bins.concat('detector_id')
nbins = 165
theta_edges = sc.linspace(dim='theta', start=0.0, stop=1.2, num=nbins, unit='deg')
wavelength_edges = sc.linspace(dim='wavelength', start=0, stop=15.0,
                               num=nbins, unit='angstrom')
binned = sample_theta.bin(theta=theta_edges.to(unit='rad'), wavelength=wavelength_edges)
binned
binned.bins.sum().plot().save('assets/binned.png')

interactive_data = pp.data.data3d()