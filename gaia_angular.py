import streamlit as st
import pandas as pd
from uncertainties import ufloat
from uncertainties.umath import sin, cos, sqrt, asin, radians, degrees
from astroquery.simbad import Simbad
from astroquery.gaia import Gaia
from astropy.coordinates import SkyCoord
import astropy.units as u

st.set_page_config(layout="wide")

# Angular distance calculation function using the haversine formula with uncertainties
def angular_distance_with_uncertainties(ra1_deg, dec1_deg, ra2_deg, dec2_deg,
                                        ra1_err_mas, dec1_err_mas, ra2_err_mas, dec2_err_mas):
    # Convert uncertainties from mas to degrees
    ra1_err_deg = ra1_err_mas / 3600000
    dec1_err_deg = dec1_err_mas / 3600000
    ra2_err_deg = ra2_err_mas / 3600000
    dec2_err_deg = dec2_err_mas / 3600000

    # Create ufloat variables with uncertainties
    ra1 = ufloat(ra1_deg, ra1_err_deg)
    dec1 = ufloat(dec1_deg, dec1_err_deg)
    ra2 = ufloat(ra2_deg, ra2_err_deg)
    dec2 = ufloat(dec2_deg, dec2_err_deg)

    # Convert to radians
    ra1_rad = radians(ra1)
    dec1_rad = radians(dec1)
    ra2_rad = radians(ra2)
    dec2_rad = radians(dec2)

    # Differences
    delta_ra = ra2_rad - ra1_rad
    delta_dec = dec2_rad - dec1_rad

    # Haversine formula
    a = sin(delta_dec / 2)**2 + cos(dec1_rad) * cos(dec2_rad) * sin(delta_ra / 2)**2
    c = 2 * asin(sqrt(a))
    theta_rad = c

    # Convert to arcseconds
    theta_deg = degrees(theta_rad)
    theta_arcseconds = theta_deg * 3600

    return theta_arcseconds

@st.cache_data
def query_gaia_for_star(ra, dec, radius):
    query = f"""
    SELECT
        DESIGNATION,
        SOURCE_ID,
        ra,
        ra_error,
        dec,
        dec_error,
        parallax,
        parallax_error,
        pm,
        phot_g_mean_mag,
        ruwe,
        phot_variable_flag
    FROM
        gaiadr3.gaia_source
    WHERE
        CONTAINS(
            POINT('ICRS', ra, dec),
            CIRCLE('ICRS', {ra}, {dec}, {radius})
        ) = 1
    """
    job = Gaia.launch_job(query)
    results = job.get_results()
    return results.to_pandas()

@st.cache_data
def query_simbad(star_name):
    custom_simbad = Simbad()
    custom_simbad.add_votable_fields('ra', 'dec', 'plx')
    return custom_simbad.query_object(star_name)

# Update site title and description
st.title("Star Finder Application")
st.markdown("<p style='font-size:16px'>An application to search for stars in the Gaia DR3 catalog and display nearby stars with their properties. Angular distances are calculated to the target star using the Haversine formula.</p>", unsafe_allow_html=True)

# Create a form to enable Enter key submission
with st.form(key='search_form'):
    col1, col2 = st.columns([2, 1])
    with col1:
        star_name = st.text_input("Enter Star Name:")
    with col2:
        search_radius_arcsec = st.number_input("Search Radius (arcseconds):", min_value=1, max_value=300, value=30) / 3600

    # Submit button in the form
    submitted = st.form_submit_button("Search")

if submitted:
    result_table = query_simbad(star_name)

    if result_table is None:
        st.write("Star not found.")
    else:
        ra = result_table['RA'][0]
        dec = result_table['DEC'][0]
        coord = SkyCoord(ra, dec, unit=(u.hourangle, u.deg))
        ra_deg = coord.ra.deg
        dec_deg = coord.dec.deg
        simbad_parallax = result_table['PLX_VALUE'][0] if 'PLX_VALUE' in result_table.colnames else None

        gaia_results = query_gaia_for_star(ra_deg, dec_deg, search_radius_arcsec)
        if gaia_results.empty:
            st.write("No nearby stars found in Gaia DR3.")
        else:
            variable_star = gaia_results[gaia_results['phot_variable_flag'] == 'VARIABLE']
            if not variable_star.empty:
                closest_star = variable_star.iloc[0]
            else:
                closest_star = gaia_results.iloc[(gaia_results['parallax'] - simbad_parallax).abs().argsort().iloc[0]]

            if simbad_parallax is not None and abs(closest_star['parallax'] - simbad_parallax) > 1e-2:
                st.write("No matching star found due to parallax mismatch.")
            else:
                # Prepare the closest star row
                closest_star_row = pd.DataFrame({
                    "Designation": [closest_star['DESIGNATION']],
                    "RA [deg]": [closest_star['ra']],
                    "RA Error [mas]": [closest_star['ra_error']],
                    "Dec [deg]": [closest_star['dec']],
                    "Dec Error [mas]": [closest_star['dec_error']],
                    "Parallax [mas]": [closest_star['parallax']],
                    "Parallax Error [mas]": [closest_star['parallax_error']],
                    "Proper Motion [mas yr⁻¹]": [closest_star['pm']],
                    "RUWE": [closest_star['ruwe']],
                    "Magnitude [Gaia G]": [closest_star['phot_g_mean_mag']],
                    "Angular Distance [arcsec]": [0],
                    "Angular Distance Error [arcsec]": [0]
                })

                # Remove the closest star from the results
                gaia_results = gaia_results.drop(closest_star.name)

                # Compute angular distances with uncertainties
                def compute_angular_distance(row):
                    result = angular_distance_with_uncertainties(
                        closest_star['ra'], closest_star['dec'],
                        row['ra'], row['dec'],
                        closest_star['ra_error'], closest_star['dec_error'],
                        row['ra_error'], row['dec_error']
                    )
                    return result

                gaia_results['angular_distance'] = gaia_results.apply(compute_angular_distance, axis=1)

                # Extract nominal values and uncertainties
                gaia_results['Angular Distance [arcsec]'] = gaia_results['angular_distance'].apply(lambda x: x.nominal_value)
                gaia_results['Angular Distance Error [arcsec]'] = gaia_results['angular_distance'].apply(lambda x: x.std_dev)

                # Prepare the DataFrame
                closest_stars = pd.DataFrame({
                    "Designation": gaia_results['DESIGNATION'],
                    "RA [deg]": gaia_results['ra'],
                    "RA Error [mas]": gaia_results['ra_error'],
                    "Dec [deg]": gaia_results['dec'],
                    "Dec Error [mas]": gaia_results['dec_error'],
                    "Parallax [mas]": gaia_results['parallax'],
                    "Parallax Error [mas]": gaia_results['parallax_error'],
                    "Proper Motion [mas yr⁻¹]": gaia_results['pm'],
                    "RUWE": gaia_results['ruwe'],
                    "Magnitude [Gaia G]": gaia_results['phot_g_mean_mag'],
                    "Angular Distance [arcsec]": gaia_results['Angular Distance [arcsec]'],
                    "Angular Distance Error [arcsec]": gaia_results['Angular Distance Error [arcsec]']
                })

                # Combine target star and other stars
                full_table = pd.concat([closest_star_row, closest_stars], ignore_index=True)
                full_table = full_table.sort_values(by="Angular Distance [arcsec]", ascending=True, na_position='first').reset_index(drop=True)

                # Function to highlight the first row
                def highlight_target_row(row):
                    return ['background-color: DarkGreen' if row.name == 0 else '' for _ in row]

                # Center the text in the DataFrame and apply highlighting
                styled_table = full_table.style.apply(highlight_target_row, axis=1).set_properties(**{'text-align': 'center'})

                st.write("Nearby Stars")
                st.markdown(
                    "<p style='font-size:16px; font-style:italic;'>The target star is highlighted in dark green.</p>",
                    unsafe_allow_html=True)
                st.dataframe(styled_table, use_container_width=True, hide_index=True)


