# Copyright 2020, by the California Institute of Technology. ALL RIGHTS
# RESERVED. United States Government Sponsorship acknowledged. Any
# commercial use must be negotiated with the Office of Technology Transfer
# at the California Institute of Technology.
# -------------------------------------------------------------------------

import numpy as np
import sys
sys.path.append('../')
from astropy.io import fits

import falco

mp = falco.config.ModelParameters()

###--Record Keeping
mp.SeriesNum = 867
mp.TrialNum = 5309

###--Special Computational Settings
mp.flagMultiproc = False
mp.flagPlot = False
mp.useGPU = False

###--General
mp.centering = 'pixel'

###--Whether to include planet in the images
mp.planetFlag = False;

###--Method of computing core throughput:
### - 'HMI' for energy within half-max isophote divided by energy at telescope pupil
### - 'EE' for encircled energy within a radius (mp.thput_radius) divided by energy at telescope pupil
mp.thput_metric = 'EE'; 
mp.thput_radius = 0.7 #--photometric aperture radius [lambda_c/D]. Used ONLY for 'EE' method.
mp.thput_eval_x = 7 # x location [lambda_c/D] in dark hole at which to evaluate throughput
mp.thput_eval_y = 0 # y location [lambda_c/D] in dark hole at which to evaluate throughput

###--Where to shift the source to compute the intensity normalization value.
mp.source_x_offset_norm = 7  # x location [lambda_c/D] in dark hole at which to compute intensity normalization
mp.source_y_offset_norm = 0  # y location [lambda_c/D] in dark hole at which to compute intensity normalization

#### Bandwidth and Wavelength Specs

mp.lambda0 = 550e-9    #--Central wavelength of the whole spectral bandpass [meters]
mp.fracBW = 0.10       #--fractional bandwidth of the whole bandpass (Delta lambda / lambda0)
mp.Nsbp = 5            #--Number of sub-bandpasses to divide the whole bandpass into for estimation and control
mp.Nwpsbp = 1          #--Number of wavelengths to used to approximate an image in each sub-bandpass

#### Wavefront Estimation

###--Estimator Options:
### - 'perfect' for exact numerical answer from full model
### - 'pwp-bp' for pairwise probing with batch process estimation
### - 'pwp-kf' for pairwise probing with Kalman filter [NOT TESTED YET]
### - 'pwp-iekf' for pairwise probing with iterated extended Kalman filter  [NOT AVAILABLE YET]
mp.estimator = 'perfect';

###--New variables for pairwise probing estimation:
mp.est = falco.config.Object()
mp.est.probe = falco.config.Object()
mp.est.probe.Npairs = 3;#2;     # Number of pair-wise probe PAIRS to use.
mp.est.probe.whichDM = 1;    # Which DM # to use for probing. 1 or 2. Default is 1
mp.est.probe.radius = 12;#20;    # Max x/y extent of probed region [actuators].
mp.est.probe.offsetX = 0;   # offset of probe center in x [actuators]. Use to avoid central obscurations.
mp.est.probe.offsetY = 14;    # offset of probe center in y [actuators]. Use to avoid central obscurations.
mp.est.probe.axis = 'alternate';     # which axis to have the phase discontinuity along [x or y or xy/alt/alternate]
mp.est.probe.gainFudge = 1;     # empirical fudge factor to make average probe amplitude match desired value.

###--New variables for pairwise probing with a Kalman filter
###  mp.est.ItrStartKF =  #Which correction iteration to start recursive estimate
###  mp.est.tExp =
###  mp.est.num_im =
###  mp.readNoiseStd =
###  mp.peakCountsPerPixPerSec =
###  mp.est.Qcoef =
###  mp.est.Rcoef =

#### Wavefront Control: General
mp.ctrl = falco.config.Object()

mp.ctrl.flagUseModel = True #--Perform a model-based grid search using the compact model

###--Threshold for culling weak actuators from the Jacobian:
mp.logGmin = -6;  # 10^(mp.logGmin) used on the intensity of DM1 and DM2 Jacobians to weed out the weakest actuators

###--Zernikes to suppress with controller
mp.jac = falco.config.Object()
mp.jac.zerns = np.array([1])  #--Which Zernike modes to include in Jacobian. Given as the max Noll index. Always include the value "1" for the on-axis piston mode.
mp.jac.Zcoef = 1e-9*np.ones(np.size(mp.jac.zerns)) #--meters RMS of Zernike aberrations. (piston value is reset to 1 later)
    
###--Zernikes to compute sensitivities for
mp.eval = falco.config.Object()
mp.eval.indsZnoll = np.array([2,3,4,5,6]) #--Noll indices of Zernikes to compute values for [1-D ndarray]

###--Annuli to compute 1nm RMS Zernike sensitivities over. Columns are [inner radius, outer radius]. One row per annulus.
mp.eval.Rsens = np.array([[2., 3.],[3., 4.],[4., 5.]]);  # [2-D ndarray]

###--Grid- or Line-Search Settings
mp.ctrl.log10regVec = np.arange(-6,-2+0.5,0.5) #-6:1/2:-2; #--log10 of the regularization exponents (often called Beta values)
mp.ctrl.dmfacVec = np.array([1.])            #--Proportional gain term applied to the total DM delta command. Usually in range [0.5,1]. [1-D ndarray]
### # mp.ctrl.dm9regfacVec = 1;        #--Additional regularization factor applied to DM9
   
###--Spatial pixel weighting
mp.WspatialDef = []# [3, 4.5, 3]; #--spatial control Jacobian weighting by annulus: [Inner radius, outer radius, intensity weight; (as many rows as desired)] [ndarray]

###--DM weighting
mp.dm1.weight = 1.
mp.dm2.weight = 1.

###--Voltage range restrictions
mp.dm1.maxAbsV = 1000  #--Max absolute voltage (+/-) for each actuator [volts] #--NOT ENFORCED YET
mp.dm2.maxAbsV = 1000  #--Max absolute voltage (+/-) for each actuator [volts] #--NOT ENFORCED YET
mp.maxAbsdV = 1000     #--Max +/- delta voltage step for each actuator for DMs 1 and 2 [volts] #--NOT ENFORCED YET

#### Wavefront Control: Controller Specific
### Controller options: 
###  - 'gridsearchEFC' for EFC as an empirical grid search over tuning parameters
###  - 'plannedEFC' for EFC with an automated regularization schedule
###  - 'SM-CVX' for constrained EFC using CVX. --> DEVELOPMENT ONLY
mp.controller = 'gridsearchEFC';

### # # GRID SEARCH EFC DEFAULTS     
###--WFSC Iterations and Control Matrix Relinearization
mp.Nitr = 5 #--Number of estimation+control iterations to perform
mp.relinItrVec = np.arange(0, mp.Nitr) #1:mp.Nitr;  #--Which correction iterations at which to re-compute the control Jacobian [1-D ndarray]
mp.dm_ind = np.array([1,2]) #[1, 2]; #--Which DMs to use [1-D ndarray]

### # # PLANNED SEARCH EFC DEFAULTS     
### mp.dm_ind = [1 2 ]; # vector of DMs used in controller at ANY time (not necessarily all at once or all the time). 
### mp.ctrl.dmfacVec = 1;
### #--CONTROL SCHEDULE. Columns of mp.ctrl.sched_mat are: 
###     # Column 1: # of iterations, 
###     # Column 2: log10(regularization), 
###     # Column 3: which DMs to use (12, 128, 129, or 1289) for control
###     # Column 4: flag (0 = False, 1 = True), whether to re-linearize
###     #   at that iteration.
###     # Column 5: flag (0 = False, 1 = True), whether to perform an
###     #   EFC parameter grid search to find the set giving the best
###     #   contrast .
###     # The imaginary part of the log10(regularization) in column 2 is
###     #  replaced for that iteration with the optimal log10(regularization)
###     # A row starting with [0, 0, 0, 1...] is for relinearizing only at that time
### 
### mp.ctrl.sched_mat = [...
###     repmat([1,1j,12,1,1],[4,1]);...
###     repmat([1,1j-1,12,1,1],[25,1]);...
###     repmat([1,1j,12,1,1],[1,1]);...
###     ];
### [mp.Nitr, mp.relinItrVec, mp.gridSearchItrVec, mp.ctrl.log10regSchedIn, mp.dm_ind_sched] = falco_ctrl_EFC_schedule_generator(mp.ctrl.sched_mat);


### Deformable Mirrors: Influence Functions
##--Influence Function Options:
## - falco.INFLUENCE_XINETICS uses the file 'influence_dm5v2.fits' for one type of Xinetics DM
## - INFLUENCE_BMC_2K uses the file 'influence_BMC_2kDM_400micron_res10.fits' for BMC 2k DM
## - INFLUENCE_BMC_KILO uses the file 'influence_BMC_kiloDM_300micron_res10_spline.fits' for BMC kiloDM

mp.dm1.inf_fn = falco.INFLUENCE_XINETICS
mp.dm2.inf_fn = falco.INFLUENCE_XINETICS

mp.dm1.dm_spacing = 400e-6 #--User defined actuator pitch
mp.dm2.dm_spacing = 400e-6 #--User defined actuator pitch

mp.dm1.inf_sign = '+'
mp.dm2.inf_sign = '+'

### Deformable Mirrors: Optical Layout Parameters

##--DM1 parameters
mp.dm1.Nact = 64               # # of actuators across DM array
mp.dm1.VtoH = 1e-9*np.ones((64, 64))  # gains of all actuators [nm/V of free stroke]
mp.dm1.xtilt = 0               # for foreshortening. angle of rotation about x-axis [degrees]
mp.dm1.ytilt = 0               # for foreshortening. angle of rotation about y-axis [degrees]
mp.dm1.zrot = 0;               # clocking of DM surface [degrees]
mp.dm1.xc = (64/2 - 1/2)       # x-center location of DM surface [actuator widths]
mp.dm1.yc = (64/2 - 1/2)       # y-center location of DM surface [actuator widths]
mp.dm1.edgeBuffer = 1          # max radius (in actuator spacings) outside of beam on DM surface to compute influence functions for. [actuator widths]

##--DM2 parameters
mp.dm2.Nact = 64;               # # of actuators across DM array
mp.dm2.VtoH = 1e-9*np.ones((64, 64))  # gains of all actuators [nm/V of free stroke]
mp.dm2.xtilt = 0;               # for foreshortening. angle of rotation about x-axis [degrees]
mp.dm2.ytilt = 0                # for foreshortening. angle of rotation about y-axis [degrees]
mp.dm2.zrot = 0                 # clocking of DM surface [degrees]
mp.dm2.xc = (64/2 - 1/2)        # x-center location of DM surface [actuator widths]
mp.dm2.yc = (64/2 - 1/2)        # y-center location of DM surface [actuator widths]
mp.dm2.edgeBuffer = 1          # max radius (in actuator spacings) outside of beam on DM surface to compute influence functions for. [actuator widths]

##--Aperture stops at DMs
mp.flagDM1stop = False #--Whether to apply an iris or not
mp.dm1.Dstop = 100e-3;  #--Diameter of iris [meters]
mp.flagDM2stop = False  #--Whether to apply an iris or not
mp.dm2.Dstop = 50e-3;   #--Diameter of iris [meters]

##--DM separations
mp.d_P2_dm1 = 0        # distance (along +z axis) from P2 pupil to DM1 [meters]
mp.d_dm1_dm2 = 0.32   # distance between DM1 and DM2 [meters]


### Optical Layout: All models

##--Key Optical Layout Choices
mp.flagSim = True      #--Simulation or not
mp.layout = 'proper';  #--Which optical layout to use
mp.coro = 'vortex'
mp.flagApod = False
mp.flagDMwfe = False

####### NEED TO DETERMINE
mp.Fend = falco.config.Object()

##--Final Focal Plane Properties
mp.Fend.res = 3 #--Sampling [ pixels per lambda0/D]
mp.Fend.FOV = 30 #--half-width of the field of view in both dimensions [lambda0/D]

####### NEED TO DETERMINE
##--Correction and scoring region definition
mp.Fend.corr = falco.config.Object()
mp.Fend.corr.Rin = 2.0   # inner radius of dark hole correction region [lambda0/D]
mp.Fend.corr.Rout  = 26  # outer radius of dark hole correction region [lambda0/D]
mp.Fend.corr.ang  = 180  # angular opening of dark hole correction region [degrees]
#
mp.Fend.score = falco.config.Object()
mp.Fend.score.Rin = 2.0  # inner radius of dark hole scoring region [lambda0/D]
mp.Fend.score.Rout = 26  # outer radius of dark hole scoring region [lambda0/D]
mp.Fend.score.ang = 180  # angular opening of dark hole scoring region [degrees]
#
mp.Fend.sides = 'both' #--Which side(s) for correction: 'both', 'left', 'right', 'top', 'bottom'

### Optical Layout: Compact Model (and Jacobian Model)

##--Focal Lengths
mp.fl = 1. #--[meters] Focal length value used for all FTs in the compact model. Don't need different values since this is a Fourier model.

##--Pupil Plane Diameters
mp.P2.D = 60.8985*mp.dm1.dm_spacing
mp.P3.D = mp.P2.D
mp.P4.D = mp.P2.D

####### NEED TO DETERMINE
##--Pupil Plane Resolutions
mp.P1.compact.Nbeam = 62*4
#mp.P2.compact.Nbeam = mp.P1.compact.Nbeam
#mp.P3.compact.Nbeam = mp.P1.compact.Nbeam
mp.P4.compact.Nbeam = mp.P1.compact.Nbeam  # P4 size must be the same as P1 for Vortex. 

##--Number of re-imaging relays between pupil planesin compact model. Needed
## to keep track of 180-degree rotations compared to the full model, which 
## in general can have probably has extra collimated beams compared to the
## compact model.
mp.Nrelay1to2 = 1
mp.Nrelay2to3 = 1
mp.Nrelay3to4 = 1
mp.NrelayFend = 0 #--How many times to rotate the final image by 180 degrees

#mp.F3.compact.res = 6    # sampling of FPM for full model [pixels per lambda0/D]

### Optical Layout: Full Model 

##--Focal Lengths
## mp.fl = 1; 
#

##--Pupil Plane Resolutions
mp.P1.full.Nbeam = 250
#mp.P2.full.Nbeam = 250
#mp.P3.full.Nbeam = 250
mp.P4.full.Nbeam = 250 # P4 size must be the same as P1 for Vortex.

#mp.F3.full.res = 6    # sampling of FPM for full model [pixels per lambda0/D]

### Mask Definitions
mp.full = falco.config.Object() #--Initialize
mp.compact = falco.config.Object() #--Initialize

# %% Optical Layout: Full Model 

mp.full.flagPROPER = True #--Whether the full model is a PROPER prescription
mp.full.prescription = 'habex'
# mp.full.cor_type = 'vortex' 
mp.full.map_dir = '/Users/ajriggs/Documents/habex/maps/' #-- directory containing optical surface error maps

#--Focal planes
mp.full.nout = falco.util.ceil_even(1 + mp.Fend.res*(2*mp.Fend.FOV)) #  dimensions of output in pixels (overrides output_dim0)
mp.full.final_sampling_lam0 = 1/mp.Fend.res #   final sampling in lambda0/D
mp.full.use_field_stop = True #-- use field stop (0 = no stop)
mp.full.field_stop_radius = mp.Fend.corr.Rout #-- field stop radius in lam0/D

#--Pupil Plane Resolutions
mp.P1.full.Nbeam = 62*7
mp.P1.full.Narr = int(2**falco.util.nextpow2(mp.P1.full.Nbeam))
mp.full.lambda0_um = mp.lambda0*1e6 #-- default reference wavelength (center of bandpass) for star offsets & field stop size
mp.full.pupil_diam_pix = mp.P1.full.Nbeam

mp.full.use_errors = True
mp.full.dm1FlatMap = fits.getdata(mp.full.map_dir+'flat_map.fits')
mp.full.dm2FlatMap = 0

# % mp.full.zindex = 4;
# % mp.full.zval_m = 0.19e-9;
# % mp.full.use_hlc_dm_patterns = false; % whether to use design WFE maps for HLC.
# % mp.full.lambda0_m = mp.lambda0;
# % mp.full.input_field_rootname = '';	%   rootname of files containing aberrated pupil
# % mp.full.use_dm1 = 0;                %   use DM1? 1 or 0
# % mp.full.use_dm2 = 0;                %   use DM2? 1 or 0
# % mp.full.dm_sampling_m = 0.9906e-3;     %   actuator spacing in meters; default is 1 mm
# % mp.full.dm1_xc_act = 23.5;          %   for 48x48 DM, wavefront centered at actuator intersections: (0,0) = 1st actuator center
# % mp.full.dm1_yc_act = 23.5;
# % mp.full.dm1_xtilt_deg = 0;   		%   tilt around X axis
# % mp.full.dm1_ytilt_deg = 5.7;		%   effective DM tilt in deg including 9.65 deg actual tilt and pupil ellipticity
# % mp.full.dm1_ztilt_deg = 0;
# % mp.full.dm2_xc_act = 23.5;		
# % mp.full.dm2_yc_act = 23.5;
# % mp.full.dm2_xtilt_deg = 0;   
# % mp.full.dm2_ytilt_deg = 5.7;
# % mp.full.dm2_ztilt_deg = 0;
# % mp.full.use_fpm  = 1;


# %% Mask Definitions

#--Pupil definition
mp.whichPupil = 'simpleproper'
mp.P1.IDnorm = 0.00 #--ID of the central obscuration [diameter]. Used only for computing the RMS DM surface from the ID to the OD of the pupil. OD is assumed to be 1.
mp.P1.ODnorm = 1.00 # Outer diameter of the telescope [diameter]
mp.P1.D = 4.0 #--telescope diameter [meters]. Used only for converting milliarcseconds to lambda0/D or vice-versa.
mp.P1.Nstrut = 0
mp.P1.angStrut = []
mp.P1.wStrut = 0
mp.P1.stretch = 1

#--Lyot stop padding
mp.P4.IDnorm = 0 #--Lyot stop ID [Dtelescope]
mp.P4.ODnorm = 0.95 #--Lyot stop OD [Dtelescope]
mp.P4.padFacPct = 0
mp.P4.Nstrut = 0
mp.P4.angStrut = []
mp.P4.wStrut = 0
mp.P4.stretch = 1

#--Whether to generate or load various masks: compact model
# mp.dm1.wfe = fitsread([mp.full.data_dir 'hlc_20190210/' 'run461_dm1wfe.fits']);
# mp.dm2.wfe = fitsread([mp.full.data_dir 'hlc_20190210/' 'run461_dm2wfe.fits']);

# %% VC-Specific Values %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

mp.F3.VortexCharge = 6 #--Charge of the vortex mask

# %%
#-- Values for PROPER
mp.full.normLyotDiam = mp.P4.ODnorm
mp.full.vortexCharge = mp.F3.VortexCharge
