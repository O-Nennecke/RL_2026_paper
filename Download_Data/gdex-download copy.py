#!/usr/bin/env python
""" 
Python script to download selected files from gdex.ucar.edu.
After you save the file, don't forget to make it executable
i.e. - "chmod 755 <name_of_script>"
"""
import sys, os
from urllib.request import build_opener

opener = build_opener()

filelist = [
  'https://osdf-director.osg-htc.org/ncar/gdex/d651056/CESM2-LE/atm/proc/tseries/day_1/FSDS/b.e21.BSSP370smbb.f09_g17.LE2-1011.001.cam.h1.FSDS.20650101-20741231.nc',
  'https://osdf-director.osg-htc.org/ncar/gdex/d651056/CESM2-LE/atm/proc/tseries/day_1/FSDS/b.e21.BSSP370cmip6.f09_g17.LE2-1251.006.cam.h1.FSDS.20350101-20441231.nc',
  'https://osdf-director.osg-htc.org/ncar/gdex/d651056/CESM2-LE/atm/proc/tseries/day_1/FSDS/b.e21.BSSP370cmip6.f09_g17.LE2-1301.010.cam.h1.FSDS.20850101-20941231.nc'
]
from http.client import IncompleteRead
import sys, os, time
counter = 0

for file in filelist:
    counter += 1
    ofile = os.path.basename(file)
    if os.path.exists(ofile):
      # print(f"{ofile} already exists — skipping")
      continue
    parts = ofile.split(".")
    time_range = parts[9]
    if time_range not in ["20150101-20241231", "20350101-20441231", "20450101-20541231"]:
        # print(f"{ofile} is not from 2015 or 2035 or 2045 — skipping")
        continue

    # sys.stdout.write("File Nr " + str(counter) + " downloading " + ofile + " ... ")
    # sys.stdout.flush()
    # infile = opener.open(file)
    # outfile = open(ofile, "wb")
    # outfile.write(infile.read())
    # outfile.close()
    # sys.stdout.write("done\n")

    # Retry loop
    while True:
        try:
            sys.stdout.write(f"File Nr {counter} downloading {ofile} ... ")
            sys.stdout.flush()

            infile = opener.open(file)
            outfile = open(ofile, "wb")
            outfile.write(infile.read())
            outfile.close()
            sys.stdout.write("done\n")
            break  # success → next file

        except IncompleteRead as e:
            sys.stdout.write(f"\nIncompleteRead: retrying {ofile}...\n")
            sys.stdout.flush()
            time.sleep(5)  # wait a few seconds before retry
        except Exception as e:
            sys.stdout.write(f"\nError downloading {ofile}: {e}\nRetrying...\n")
            sys.stdout.flush()
            time.sleep(5)
