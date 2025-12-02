# Master Thesis

This is the repository for the master thesis of Onno Nennecke

Title:

Investigation of meteorological conditions leading to extreme variable renewable energy shortage events in Germany

Abstract:

The pursuit of a climate-neutral future accelerates the expansion of renewable
energy sources such as wind and solar power. One issue with these technologies
is their dependence on favourable weather conditions. Especially critical for grid
stability are periods of extremely low renewable energy production and a coincid-
ing high demand, so-called variable renewable energy shortages (VRES). VRES
are commonly studied with observational data, which only represent one possible
realisation of internal climate variability and are therefore not sufficient to ade-
quately study extreme VRES. In this study, I validate a simple energy model and
apply it to 1000 years of climate data from different Earth System Models (ESMs)
and ERA5 reanalysis data for Germany. The model outputs are analysed with
regard to seasonality, event magnitude, behaviour, duration, composition, and
large-scale weather regimes. The event characteristics and formation mechanisms
are in-depth analysed with a case study of an exemplary VRES that occurred on
6 November 2024. It is found that VRES events exhibit a pronounced seasonality,
with both occurrence and magnitude peaking in mid-winter. Variability in wind
speed over Germany is identified as the main driver of these events, while fluctu-
ations in incoming solar radiation contribute only marginally during the winter
months. Weather pattern clustering further supports previous findings, confirming
the dominant influence of blocked circulation regimes in the formation of VRES
over Germany. The most extreme fixed-length VRES derived from ESM data
are up to 6.5 % (1-day events) and 8.8 % (7-day events) more severe than those
identified from reanalysis data. These results provide robust metrics for energy
system planners and contribute to a deeper understanding of the climatic drivers
behind low-renewable periods.

The complete thesis is available on request from the author.

## Info

1. Download Data from MaStr
2. Download climate model data with download_v2.ipynb
3. Download ERA5 data
4. Download fit and population data from vdW
5. Download data from SMARD
6. Run files in SEM_Preparation folder
7. Optionally run files in Var_Preprocessing_and_Bias_analysis folder 
8. Run SEM_application.ipynb
9. Linearly correct results with LR_adj_and_smard script
10. Run PSL_cluster
11. Run LEE_Detection
12. Analyse results with RL_data_analysis, LEE_Results_Analysis
13. Validate model with ERA5_SMARD_Comparison folder
14. Create plots with scripts in Plotting_Code folder


## Supervisors:

Dr. Peter Pfleiderer and Jun.-Prof. Dr. Sebastian Sippel  
Faculty of Physics and Earth System Sciences  
Institute for Meteorology


## Contact

Onno Nennecke: [ae06ebug@studserv.uni-leipzig.de](ae06ebug@studserv.uni-leipzig.de)

# License
[MIT](https://github.com/O-Nennecke/master_thesis/blob/main/LICENSE)
