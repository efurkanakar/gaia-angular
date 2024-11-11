Gaia Query Application
This repository contains a Streamlit application that queries the Gaia DR3 catalog for nearby stars and computes various properties, including angular separations and corrected distances from Earth by applying parallax zero-point corrections as per Lindegren et al. (2021). The application also intelligently selects the target star based on variable star status and parallax comparison with SIMBAD data.

Table of Contents
Features
Installation
Usage
Target Star Selection Logic
Dependencies
Acknowledgements
License
Features
Queries the SIMBAD database to retrieve the coordinates and parallax of a specified star.
Searches the Gaia DR3 catalog for nearby stars within a user-defined radius.
Calculates angular distances between the target star and nearby stars using the Haversine formula with uncertainties.
Applies parallax zero-point corrections to Gaia data as per Lindegren et al. (2021).
Displays a sorted table of nearby stars, including corrected parallaxes and distances.
Highlights the target star in the output for easy identification.
Installation
Clone the repository:

bash
Kodu kopyala
git clone https://github.com/yourusername/gaia-query-app.git
cd gaia-query-app
Create a virtual environment (optional but recommended):

bash
Kodu kopyala
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
Install the required packages:

bash
Kodu kopyala
pip install -r requirements.txt
Note: Ensure that you have the zero_point module available, as it's required for the parallax zero-point correction.

Usage
Run the Streamlit application using:

bash
Kodu kopyala
streamlit run app.py
This will open the application in your default web browser.

Target Star Selection Logic
An essential feature of this application is the intelligent selection of the target star from Gaia DR3 data based on SIMBAD information and certain criteria. The selection process is as follows:

Retrieve Target Star Data from SIMBAD:

The application first queries the SIMBAD database using the provided star name.
It retrieves the Right Ascension (RA), Declination (Dec), and parallax value of the star.
Query Gaia DR3 Catalog for Nearby Stars:

Using the coordinates from SIMBAD, the application searches the Gaia DR3 catalog for stars within a user-defined radius.
Define Parallax Threshold:

A parallax difference threshold is calculated to determine acceptable matches between Gaia and SIMBAD parallax values.
The threshold is defined as the maximum of 0.1 mas or 5% of the SIMBAD parallax value.
Select Target Star from Gaia Data:

Step 1: Check for Variable Stars:

The application filters Gaia results for stars marked as variable (phot_variable_flag == 'VARIABLE').
It computes the absolute difference between their parallaxes and the SIMBAD parallax.
If variable stars exist within the parallax threshold, the one with the smallest parallax difference is selected as the target star.
Step 2: If No Matching Variable Stars:

If no variable stars meet the criteria, the application considers all stars in the Gaia results.
It computes the absolute parallax differences for all stars.
If any stars are within the parallax threshold, the one with the smallest parallax difference is selected as the target star.
Step 3: If No Stars Match Parallax Criteria:

If no stars meet the parallax criteria, the application defaults to selecting the star with the smallest angular distance from the SIMBAD coordinates.
Rationale Behind the Selection Logic:

Preference for Variable Stars:
Since the application focuses on variable stars, it prioritizes Gaia entries marked as variable when matching with SIMBAD data.
Parallax Comparison:
Comparing parallax values ensures that the selected Gaia star corresponds to the same physical star as in SIMBAD, accounting for potential slight differences due to measurement uncertainties.
Fallback to Angular Distance:
If parallax data is insufficient or not matching, angular proximity becomes the deciding factor, assuming the closest star is likely the target.
Example Scenario:

For a star like KIC 10544976:
SIMBAD provides a parallax of approximately 1.9345 mas.
The Gaia results include a star with a parallax of 1.934524097171672 mas but not marked as variable.
Using the logic above, the application selects this star as the target because its parallax closely matches the SIMBAD value, despite not being marked as variable.
Dependencies
The application relies on several Python packages:

Streamlit: For building the interactive web application.
Pandas: For data manipulation and analysis.
Astroquery: For querying astronomical databases like SIMBAD and Gaia.
Astropy: For astronomical calculations and coordinate transformations.
Uncertainties: For calculations involving uncertainties.
ZeroPoint Module: For applying parallax zero-point corrections (ensure you have the zero_point module installed).
Ensure all dependencies are installed by running pip install -r requirements.txt.

Acknowledgements
Gaia Data: This work has made use of data from the European Space Agency (ESA) mission Gaia.
SIMBAD Database: Operated at CDS, Strasbourg, France.
Lindegren et al. (2021): For the methodology on parallax zero-point corrections.
License
This project is licensed under the MIT License - see the LICENSE file for details.
