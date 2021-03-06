;   Copyright 2019 California Institute of Technology
; ------------------------------------------------------------------

nlam = 7
bandwidth = 0.1d	;-- bandpass fractional width
lam0 = 0.825d		;-- central wavelength (microns)
minlam = lam0 * (1 - bandwidth/2)
maxlam = lam0 * (1 + bandwidth/2)
lam_array = dindgen(nlam) / (nlam-1) * (maxlam - minlam) + minlam

final_sampling = 0.1
npsf = 512

print, 'Computing unaberrated coronagraphic field'

optval = {cor_type:'spc-wide', final_sampling_lam0:final_sampling}
prop_run_multi, 'wfirst_phaseb_compact', fields, lam_array, npsf, /quiet, PASSVALUE=optval
images = abs(fields)^2
image_noab = total(images,3) / nlam

print, 'Computing aberrated coronagraphic field using DM actuator pistons'

fits_read, 'spc-wide_with_aberrations_dm1.fits', dm1
fits_read, 'spc-wide_with_aberrations_dm2.fits', dm2
optval = {cor_type:'spc-wide', use_errors:1, polaxis:10, $
	  final_sampling_lam0:final_sampling, use_dm1:1, dm1_m:dm1, use_dm2:1, dm2_m:dm2}
prop_run_multi, 'wfirst_phaseb', fields, lam_array, npsf, /quiet, PASSVALUE=optval
images = abs(fields)^2
image_ab = total(images,3) / nlam

print, 'Computing 10 lam/D offset source using compact model and default DM wavefront maps'

optval = {cor_type:'spc-wide', final_sampling_lam0:final_sampling, source_x_offset:10.0}
prop_run_multi, 'wfirst_phaseb_compact', fields, lam_array, npsf, /quiet, PASSVALUE=optval
images = abs(fields)^2
psf = total(images,3) / nlam
max_psf = max(psf)

ni_noab = image_noab / max_psf
ni_ab = image_ab / max_psf

window, xs=512*2, ys=512

showcontrast, ni_noab, final_sampling, 5.4, 20, /circ, /mat, grid=512, min=1e-10, max=1e-7, mag=1
xyouts, 256, 490, 'Unaberrated', charsize=1.5, align=0.5, /dev
showcontrast, ni_ab, final_sampling, 5.4, 20, /circ, /mat, grid=512, min=1e-10, max=1e-7, xoff=512, mag=1
xyouts, 512+256, 490, 'Aberrated+DM pistons', charsize=1.5, align=0.5, /dev

end
