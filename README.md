<h1>Gaia Query: Calculating Distances and Angular Separations</h1>

<p>This repository contains a Streamlit application that queries the Gaia DR3 catalog for nearby objects and computes various properties, including angular separations and corrected distances from Earth by applying parallax zero-point corrections as per Lindegren et al. (2021). The application selects the target object based on Gaia DR3 designation availability, variable object status, and parallax comparison with SIMBAD data. The results include clear color-coded indications for the method used to identify the target object.</p>

<h2>Quick Start</h2>

<p>To use this application immediately, visit the following link and start querying Gaia DR3 data directly from your browser:</p>
<a href="https://gaia-object-distance.streamlit.app/" target="_blank">Gaia Query: Calculating Distances and Angular Separations</a>

<h2>Table of Contents</h2>
<ul>
    <li><a href="#features">Features</a></li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#target-object-selection-logic">Target Object Selection Logic</a></li>
    <li><a href="#returned-columns">Returned Columns</a></li>
    <li><a href="#dependencies">Dependencies</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
    <li><a href="#license">License</a></li>
</ul>

<h2 id="features">Features</h2>
<ul>
    <li>Calculates angular separations between two objects using the Haversine formula.</li>
    <li>Computes corrected distances using Lindegren et al. (2021) parallax zero-point corrections.</li>
</ul>

<h2 id="installation">Installation</h2>
<ol>
    <li>Clone the repository:
        <pre><code>git clone https://github.com/yourusername/gaia-query-app.git
cd gaia-query-app</code></pre>
    </li>
    <li>Create a virtual environment (optional but recommended):
        <pre><code>python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate</code></pre>
    </li>
    <li>Install the required packages:
        <pre><code>pip install -r requirements.txt</code></pre>
        <p><strong>Note:</strong> Ensure that you have the <code>zero_point</code> module available, as it's required for the parallax zero-point correction.</p>
    </li>
</ol>

<h2 id="usage">Usage</h2>
<p>To run the application locally, use the following command:</p>
<pre><code>streamlit run app.py</code></pre>
<p>This will open the application in your default web browser.</p>

<h2 id="target-object-selection-logic">Target Object Selection Logic</h2>
<p>An essential feature of this application is the intelligent selection of the target object from Gaia DR3 data based on SIMBAD information and specific criteria. The selection process is designed to ensure accurate identification of the target object, with a color-coded highlight for each method. The steps are as follows:</p>

<ol>
    <li><strong>Retrieve Target Object Data from SIMBAD:</strong>
        <ul>
            <li>The application queries the SIMBAD database using the provided object name.</li>
            <li>It retrieves the Right Ascension (RA), Declination (Dec), and parallax value of the object.</li>
            <li>If available, the Gaia DR3 designation from SIMBAD is prioritized.</li>
        </ul>
    </li>
    <li><strong>Select Target Object from Gaia Data Based on Priority Criteria:</strong>
        <ol>
            <li><strong>Step 1: Use Gaia DR3 Designation (if available):</strong>
                <ul>
                    <li>If SIMBAD provides a Gaia DR3 designation, the application directly queries Gaia DR3 with this designation.</li>
                    <li>The object is highlighted in <span style="color:green;">green</span>, indicating the most reliable method.</li>
                </ul>
            </li>
            <li><strong>Step 2: Use Parallax and Variable Object Criteria:</strong>
                <ul>
                    <li>If the Gaia DR3 designation is unavailable, the application searches for nearby Gaia DR3 objects using the coordinates from SIMBAD within a user-defined radius.</li>
                    <li>If SIMBAD provides a parallax value, the Gaia results are filtered for objects marked as variable (<code>phot_variable_flag == 'VARIABLE'</code>) and with parallax values close to the SIMBAD value.</li>
                    <li>The object is highlighted in <span style="color:orange;">orange</span>, indicating a reliable selection.</li>
                </ul>
            </li>
            <li><strong>Step 3: Consider All Objects by Parallax (if no variables match):</strong>
                <ul>
                    <li>If no variable objects meet the parallax criteria, all nearby Gaia objects are considered.</li>
                    <li>The object with the smallest parallax difference within the threshold is selected as the target and highlighted in <span style="color:red;">red</span>.</li>
                </ul>
            </li>
            <li><strong>Step 4: Fallback to Angular Distance:</strong>
                <ul>
                    <li>If no Gaia objects meet the parallax criteria, the application selects the object with the smallest angular distance from the SIMBAD coordinates as the target.</li>
                    <li>The object is highlighted in <span style="color:purple;">purple</span>, indicating the least reliable method.</li>
                </ul>
            </li>
        </ol>
    </li>
</ol>

<h2 id="returned-columns">Returned Columns</h2>

<p>The application returns the following columns from the Gaia DR3 catalog, along with their corresponding units:</p>

<table>
    <thead>
        <tr>
            <th>Column Name</th>
            <th>Description</th>
            <th>Units</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><code>Designation</code></td>
            <td>Designation of the object in the Gaia catalog.</td>
            <td>-</td>
        </tr>
        <tr>
            <td><code>RA [deg]</code></td>
            <td>Right Ascension (RA) of the object.</td>
            <td>degrees</td>
        </tr>
        <tr>
            <td><code>RA Error [mas]</code></td>
            <td>Uncertainty in Right Ascension.</td>
            <td>milliarcseconds (mas)</td>
        </tr>
        <tr>
            <td><code>Dec [deg]</code></td>
            <td>Declination (Dec) of the object.</td>
            <td>degrees</td>
        </tr>
        <tr>
            <td><code>Dec Error [mas]</code></td>
            <td>Uncertainty in Declination.</td>
            <td>milliarcseconds (mas)</td>
        </tr>
        <tr>
            <td><code>Plx [mas]</code></td>
            <td>Parallax of the object.</td>
            <td>milliarcseconds (mas)</td>
        </tr>
        <tr>
            <td><code>Plx Error [mas]</code></td>
            <td>Uncertainty in parallax.</td>
            <td>milliarcseconds (mas)</td>
        </tr>
        <tr>
            <td><code>Plx Zero-point [mas]</code></td>
            <td>Parallax zero-point correction.</td>
            <td>milliarcseconds (mas)</td>
        </tr>
        <tr>
            <td><code>Corr Plx [mas]</code></td>
            <td>Corrected parallax after applying zero-point correction.</td>
            <td>milliarcseconds (mas)</td>
        </tr>
        <tr>
            <td><code>Corr Plx Err [mas]</code></td>
            <td>Uncertainty in the corrected parallax.</td>
            <td>milliarcseconds (mas)</td>
        </tr>
        <tr>
            <td><code>Distance [pc]</code></td>
            <td>Distance to the object in parsecs.</td>
            <td>parsecs (pc)</td>
        </tr>
        <tr>
            <td><code>Distance Err [pc]</code></td>
            <td>Uncertainty in the distance to the object.</td>
            <td>parsecs (pc)</td>
        </tr>
        <tr>
            <td><code>Angular Distance [arcsec]</code></td>
            <td>Angular separation between the target object and a reference object.</td>
            <td>arcseconds (arcsec)</td>
        </tr>
        <tr>
            <td><code>Angular Distance Error [arcsec]</code></td>
            <td>Uncertainty in the angular separation.</td>
            <td>arcseconds (arcsec)</td>
        </tr>
        <tr>
            <td><code>Linear Separation [AU]</code></td>
            <td>Linear (physical) separation between objects in Astronomical Units (AU).</td>
            <td>Astronomical Units (AU)</td>
        </tr>
        <tr>
            <td><code>Linear Separation Err [AU]</code></td>
            <td>Uncertainty in the linear separation.</td>
            <td>Astronomical Units (AU)</td>
        </tr>
        <tr>
            <td><code>Proper Motion [mas yr⁻¹]</code></td>
            <td>Proper motion of the object in milliarcseconds per year.</td>
            <td>milliarcseconds per year (mas yr⁻¹)</td>
        </tr>
        <tr>
            <td><code>RUWE</code></td>
            <td>Renormalized Unit Weight Error</td>
            <td>-</td>
        </tr>
        <tr>
            <td><code>Magnitude [Gaia G]</code></td>
            <td>Mean magnitude of the object in the Gaia G-band.</td>
            <td>mag</td>
        </tr>
        <tr>
            <td><code>Eff Temp [K]</code></td>
            <td>Effective temperature of the object.</td>
            <td>K (Kelvin)</td>
        </tr>
        <tr>
            <td><code>Eff Temp Err [K]</code></td>
            <td>Uncertainty in the effective temperature.</td>
            <td>K (Kelvin)</td>
        </tr>
    </tbody>
</table>

<h2 id="dependencies">Dependencies</h2>
<ul>
    <li>streamlit</li>
    <li>pandas</li>
    <li>astroquery</li>
    <li>astropy</li>
    <li>uncertainties</li>
    <li>numpy==1.26.4</li>
    <li>zero_point</li>
</ul>

<h2 id="acknowledgements">Acknowledgements</h2>
<ul>
    <li><strong>Gaia Data:</strong> This work has made use of data from the European Space Agency (ESA) mission Gaia.</li>
    <li><strong>SIMBAD Database:</strong> Operated at CDS, Strasbourg, France.</li>
    <li><strong>Lindegren et al. (2021):</strong> For the methodology on parallax zero-point corrections.</li>
</ul>

<h2 id="license">License</h2>
<p>This project is licensed under the Apache License 2.0 - see the <a href="LICENSE">LICENSE</a> file for details.</p>
