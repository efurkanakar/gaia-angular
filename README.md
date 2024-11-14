<h1>Gaia Query: Calculating Distances and Angular Separations</h1>

<p>This repository contains a Streamlit application that queries the Gaia DR3 catalog for nearby objects and computes various properties, including angular separations and corrected distances from Earth by applying parallax zero-point corrections as per Lindegren et al. (2021). The application also intelligently selects the target object based on Gaia DR3 designation availability, variable object status, and parallax comparison with SIMBAD data.</p>

<h2>Quick Start</h2>

<p>To use this application immediately, visit the following link and start querying Gaia DR3 data directly from your browser:</p>
<a href="https://gaia-object-distance.streamlit.app/" target="_blank">Gaia Query: Calculating Distances and Angular Separations</a>

<h2>Table of Contents</h2>
<ul>
    <li><a href="#features">Features</a></li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#target-object-selection-logic">Target Object Selection Logic</a></li>
    <li><a href="#dependencies">Dependencies</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
    <li><a href="#license">License</a></li>
</ul>

<h2 id="features">Features</h2>
<ul>
    <li><strong>SIMBAD Database Query:</strong> Retrieves coordinates (RA and Dec) and parallax of a specified object from the SIMBAD database.</li>
    <li><strong>Gaia DR3 Catalog Search:</strong> Searches for nearby objects within a user-defined radius in the Gaia DR3 catalog.</li>
    <li><strong>Angular Distance Calculation:</strong> Calculates angular distances between the target object and nearby objects using the Haversine formula, including uncertainties.</li>
    <li><strong>Parallax Zero-Point Correction:</strong> Applies parallax zero-point corrections to Gaia data as per Lindegren et al. (2021).</li>
    <li><strong>Intelligent Target Object Selection:</strong> Selects the target object from Gaia data based on Gaia DR3 designation, variable object status, and parallax comparison with SIMBAD data.</li>
    <li><strong>Results Display:</strong> Presents a sorted table of nearby objects, including corrected parallaxes, distances, and angular separations, with the target object highlighted.</li>
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
<p>An essential feature of this application is the intelligent selection of the target object from Gaia DR3 data based on SIMBAD information and specific criteria. The selection process is designed to ensure accurate identification of the target object. The steps are as follows:</p>

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
                    <li>If the Gaia DR3 entry exists, this object is chosen as the target, and other steps are skipped.</li>
                </ul>
            </li>
            <li><strong>Step 2: Use Parallax and Variable Object Criteria:</strong>
                <ul>
                    <li>If the Gaia DR3 designation is unavailable, the application searches for nearby Gaia DR3 objects using the coordinates from SIMBAD within a user-defined radius.</li>
                    <li>If SIMBAD provides a parallax value, the Gaia results are filtered for objects marked as variable (<code>phot_variable_flag == 'VARIABLE'</code>) and with parallax values close to the SIMBAD value.</li>
                    <li>The application uses a parallax threshold defined as the maximum of <strong>0.1 mas</strong> or <strong>5%</strong> of the SIMBAD parallax value.</li>
                    <li>If variable objects within this threshold exist, the object with the smallest parallax difference is selected as the target.</li>
                </ul>
            </li>
            <li><strong>Step 3: Consider All Objects by Parallax (if no variables match):</strong>
                <ul>
                    <li>If no variable objects meet the parallax criteria, all nearby Gaia objects are considered.</li>
                    <li>The object with the smallest parallax difference within the threshold is selected as the target.</li>
                </ul>
            </li>
            <li><strong>Step 4: Fallback to Angular Distance:</strong>
                <ul>
                    <li>If no Gaia objects meet the parallax criteria, the application selects the object with the smallest angular distance from the SIMBAD coordinates as the target.</li>
                </ul>
            </li>
        </ol>
    </li>
</ol>

<h3>Rationale Behind the Selection Logic</h3>
<ul>
    <li><strong>Preference for Gaia DR3 Designation:</strong> Directly matching a Gaia DR3 designation ensures the highest accuracy.</li>
    <li><strong>Preference for Variable Objects:</strong> When matching with SIMBAD data, the application prioritizes Gaia entries marked as variable.</li>
    <li><strong>Parallax Comparison:</strong> Ensures the selected Gaia object corresponds to the same physical object as in SIMBAD.</li>
    <li><strong>Fallback to Angular Distance:</strong> If parallax data is insufficient or does not match, angular proximity becomes the deciding factor.</li>
</ul>

<h3>Example Scenario</h3>
<p>For an object like <strong>KIC 10544976</strong>:</p>
<ul>
    <li>SIMBAD provides a Gaia DR3 designation, which is found in the Gaia catalog.</li>
    <li>The Gaia object with this designation is selected as the target immediately, skipping further criteria.</li>
</ul>

<h2 id="dependencies">Dependencies</h2>
<p>The application relies on several Python packages:</p>
<ul>
    <li><strong>Streamlit:</strong> For building the interactive web application.</li>
    <li><strong>Pandas:</strong> For data manipulation and analysis.</li>
    <li><strong>Astroquery:</strong> For querying astronomical databases like SIMBAD and Gaia.</li>
    <li><strong>Astropy:</strong> For astronomical calculations and coordinate transformations.</li>
    <li><strong>Uncertainties:</strong> For calculations involving uncertainties.</li>
    <li><strong>ZeroPoint Module:</strong> For applying parallax zero-point corrections (ensure you have the <code>zero_point</code> module installed).</li>
</ul>
<p>Ensure all dependencies are installed by running:</p>
<pre><code>pip install -r requirements.txt</code></pre>

<h2 id="acknowledgements">Acknowledgements</h2>
<ul>
    <li><strong>Gaia Data:</strong> This work has made use of data from the European Space Agency (ESA) mission Gaia.</li>
    <li><strong>SIMBAD Database:</strong> Operated at CDS, Strasbourg, France.</li>
    <li><strong>Lindegren et al. (2021):</strong> For the methodology on parallax zero-point corrections.</li>
</ul>

<h2 id="license">License</h2>
<p>This project is licensed under the Apache License 2.0 - see the <a href="LICENSE">LICENSE</a> file for details.</p>
