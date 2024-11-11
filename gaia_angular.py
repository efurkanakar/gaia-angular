import streamlit as st
import pandas as pd
from uncertainties import ufloat
from uncertainties.umath import sin, cos, sqrt, asin, radians, degrees
from astroquery.simbad import Simbad
from astroquery.gaia import Gaia
from astropy.coordinates import SkyCoord, GeocentricTrueEcliptic
import astropy.units as u
from zero_point import zpt

st.set_page_config(layout="wide")


zpt.load_tables()


def angular_distance_with_uncertainties(ra1_deg, dec1_deg, ra2_deg, dec2_deg,
                                        ra1_err_mas, dec1_err_mas, ra2_err_mas, dec2_err_mas):
    ra1_err_deg = ra1_err_mas / 3600000
    dec1_err_deg = dec1_err_mas / 3600000
    ra2_err_deg = ra2_err_mas / 3600000
    dec2_err_deg = dec2_err_mas / 3600000

    ra1 = ufloat(ra1_deg, ra1_err_deg)
    dec1 = ufloat(dec1_deg, dec1_err_deg)
    ra2 = ufloat(ra2_deg, ra2_err_deg)
    dec2 = ufloat(dec2_deg, dec2_err_deg)

    delta_ra = radians(ra2 - ra1)
    delta_dec = radians(dec2 - dec1)

    #Haversine formula
    a = sin(delta_dec / 2)**2 + cos(radians(dec1)) * cos(radians(dec2)) * sin(delta_ra / 2)**2
    theta_arcseconds = degrees(2 * asin(sqrt(a))) * 3600

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
        phot_variable_flag,
        nu_eff_used_in_astrometry,
        pseudocolour,
        astrometric_params_solved,
        ecl_lat
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


# Zero-point correction calculation as explained Lindegren et al. (2020)
def compute_zero_point_correction(row):
    phot_g_mean_mag = row['phot_g_mean_mag']
    nu_eff_used_in_astrometry = row['nu_eff_used_in_astrometry']
    pseudocolour = row['pseudocolour']
    ecl_lat = row['ecl_lat']
    astrometric_params_solved = row['astrometric_params_solved']

    # If pseudocolour is missing and it's a 5-parameter solution, set pseudocolour to 0.0
    if astrometric_params_solved == 31:
        if pd.isnull(pseudocolour):
            pseudocolour = 0.0

    # If it’s a 6-parameter solution, check for pseudocolour and reset nu_eff_used_in_astrometry to None
    elif astrometric_params_solved == 95:
        nu_eff_used_in_astrometry = None
        if pd.isnull(pseudocolour):
            st.write("Warning: Pseudocolour is required for a 6-parameter solution.")
            pseudocolour = 0.0  # Temporarily assigning 0.0 for calculation

    # If solution type is unknown, set pseudocolour and nu_eff_used_in_astrometry to None
    else:
        pseudocolour = None
        nu_eff_used_in_astrometry = None

    try:
        # Attempt zero-point calculation
        zero_point = zpt.get_zpt(phot_g_mean_mag, nu_eff_used_in_astrometry,
                                 pseudocolour, ecl_lat, astrometric_params_solved)
    except Exception as e:
        # If calculation fails, set zero_point to 0.0 and display a message
        zero_point = 0.0

    return zero_point


st.title("Gaia Query: Calculating Distances and Angular Separations")
st.markdown("""
<p style='font-size:16px'>
This application searches for objects in the Gaia DR3 catalog and displays nearby objects with their properties.
It calculates both the angular distance between stars using the Haversine formula and the corrected distance 
from Earth by applying the parallax zero-point correction as Lindegren et al. (2021).
</p>
""", unsafe_allow_html=True)

with st.form(key='search_form'):
    col1, col2 = st.columns([2, 1])
    with col1:
        star_name = st.text_input("Enter Star Name:")
    with col2:
        search_radius_arcsec = st.number_input("Search Radius (arcseconds):", min_value=1, max_value=300, value=30)

    submitted = st.form_submit_button("Search")

if submitted:
    search_radius_deg = search_radius_arcsec / 3600  # Arcseconds to degrees
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

        gaia_results = query_gaia_for_star(ra_deg, dec_deg, search_radius_deg)
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

                def compute_corrected_parallax_and_distance(row):
                    zero_point = compute_zero_point_correction(row)
                    row['parallax_zero_point'] = zero_point

                    if pd.notnull(row['parallax']) and pd.notnull(row['parallax_error']):
                        parallax = ufloat(row['parallax'], row['parallax_error'])
                        corrected_parallax = parallax - zero_point
                        distance = 1000 / corrected_parallax  # Distance in parsecs
                        row['corrected_parallax'] = corrected_parallax.nominal_value
                        row['corrected_parallax_error'] = corrected_parallax.std_dev
                        print(corrected_parallax)
                        print(row['corrected_parallax_error'])
                        row['distance_pc'] = distance.nominal_value
                        row['distance_error_pc'] = distance.std_dev
                    else:
                        row['corrected_parallax'] = None
                        row['corrected_parallax_error'] = None
                        row['distance_pc'] = None
                        row['distance_error_pc'] = None

                    return row

                closest_star = compute_corrected_parallax_and_distance(closest_star)

                gaia_results = gaia_results.apply(compute_corrected_parallax_and_distance, axis=1)

                def compute_angular_distance(row):
                    result = angular_distance_with_uncertainties(
                        closest_star['ra'], closest_star['dec'],
                        row['ra'], row['dec'],
                        closest_star['ra_error'], closest_star['dec_error'],
                        row['ra_error'], row['dec_error']
                    )
                    return result

                gaia_results['angular_distance'] = gaia_results.apply(compute_angular_distance, axis=1)

                gaia_results['Angular Distance [arcsec]'] = gaia_results['angular_distance'].apply(lambda x: x.nominal_value)
                gaia_results['Angular Distance Error [arcsec]'] = gaia_results['angular_distance'].apply(lambda x: x.std_dev)

                closest_star_row = pd.DataFrame({
                    "Designation": [closest_star['DESIGNATION']],
                    "RA [deg]": [closest_star['ra']],
                    "RA Error [mas]": [closest_star['ra_error']],
                    "Dec [deg]": [closest_star['dec']],
                    "Dec Error [mas]": [closest_star['dec_error']],
                    "Plx [mas]": [closest_star['parallax']],
                    "Plx Error [mas]": [closest_star['parallax_error']],
                    "Plx Zero-point [mas]": [closest_star['parallax_zero_point']],
                    "Corr Plx [mas]": [closest_star['corrected_parallax']],
                    "Corr Plx Err [mas]": [closest_star['corrected_parallax_error']],
                    "Distance [pc]": [closest_star['distance_pc']],
                    "Distance Err [pc]": [closest_star['distance_error_pc']],
                    "Angular Distance [arcsec]": [0],
                    "Angular Distance Err [arcsec]": [0],
                    "Proper Motion [mas yr⁻¹]": [closest_star['pm']],
                    "RUWE": [closest_star['ruwe']],
                    "Magnitude [Gaia G]": [closest_star['phot_g_mean_mag']],
                })

                gaia_results = gaia_results.drop(closest_star.name)

                closest_stars = pd.DataFrame({
                    "Designation": gaia_results['DESIGNATION'],
                    "RA [deg]": gaia_results['ra'],
                    "RA Error [mas]": gaia_results['ra_error'],
                    "Dec [deg]": gaia_results['dec'],
                    "Dec Error [mas]": gaia_results['dec_error'],
                    "Plx [mas]": gaia_results['parallax'],
                    "Plx Err [mas]": gaia_results['parallax_error'],
                    "Plx Zero-point [mas]": gaia_results['parallax_zero_point'],
                    "Corr Plx [mas]": gaia_results['corrected_parallax'],
                    "Corr Plx Err [mas]": gaia_results['corrected_parallax_error'],
                    "Distance [pc]": gaia_results['distance_pc'],
                    "Distance Err [pc]": gaia_results['distance_error_pc'],
                    "Angular Distance [arcsec]": gaia_results['Angular Distance [arcsec]'],
                    "Angular Distance Err [arcsec]": gaia_results['Angular Distance Error [arcsec]'],
                    "Proper Motion [mas yr⁻¹]": gaia_results['pm'],
                    "RUWE": gaia_results['ruwe'],
                    "Magnitude [Gaia G]": gaia_results['phot_g_mean_mag'],
                })

                full_table = pd.concat([closest_star_row, closest_stars], ignore_index=True)
                full_table = full_table.sort_values(by="Angular Distance [arcsec]", ascending=True, na_position='first').reset_index(drop=True)

                def highlight_target_row(row):
                    return ['background-color: DarkGreen' if row.name == 0 else '' for _ in row]

                styled_table = full_table.style.apply(highlight_target_row, axis=1).set_properties(**{'text-align': 'center'})

                st.write("Nearby Stars")
                st.markdown(
                    "<p style='font-size:16px; font-style:italic;'>The target star is highlighted in dark green.</p>",
                    unsafe_allow_html=True)
                st.dataframe(styled_table, use_container_width=True, hide_index=True)
