# Complete Paper Validation Report

**Date:** 2025-11-05 22:16:57.407253

## Test Results

| Test | Script | Status |
|------|--------|--------|
| Multi-wavelength IR ring extraction | RUN_COMPLETE_IR_ANALYSIS.py | PASS |
| Two-metric comparison (GR vs SSZ) | two_metric_model.py | PASS |
| Energy release mechanism | energy_release_model.py | PASS |
| LBV rings validation (momentum/velocity) | runner.py | FAIL |
| γ_seg(r) profile fitting | fit_gamma_seg_profile.py | FAIL |
| Complete SSZ model test (Sec 5.1-5.6) | test_segmented_spacetime_full.py | FAIL |
| Core mass derivation (Sec 5.5) | calculate_core_mass.py | FAIL |
| Radio redshift from temporal delay (Sec 5.4) | radio_redshift_prediction.py | FAIL |
| NH3 velocity components (Sec 5.3) | analyze_nh3_velocities.py | PASS |
| Paper predictions validation (G79) | verify_paper_predictions_FIXED.py | PASS |
| Paper predictions validation (LBV) | verify_paper_predictions_FIXED.py | PASS |
| Hybrid T-v model (Sec 6.2) | ring_temperature_to_velocity_hybrid.py | FAIL |
| Data loading and validation | data_loader.py | PASS |
| Statistical validation | validator.py | PASS |

## Paper Reference Values

- **alpha:** 0.12
- **alpha_err:** 0.03
- **r_c_pc:** 1.9
- **delta_v_kms:** 5.0
- **M_core_msun:** 8.7
- **M_core_err:** 1.5
- **T0_K:** 240
- **distance_kpc:** 1.7
- **diameter_pc:** 4.5
- **v_obs_kms:** 15.0
- **v_predicted_kms:** 10.0
