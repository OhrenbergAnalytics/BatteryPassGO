import streamlit as st
import pandas as pd
import re
import os
from pathlib import Path
from api import create_model_and_upload_data


# --- Global Style ---
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-family: 'Inter';
        font-size: 0.9rem;
    }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)


st.markdown("""
    <style>
    /* Logo-Größe kleiner & linksbündig */
    div[data-testid="stSidebarHeader"] img, div[data-testid="collapsedControl"] img {
        height: 80px !important;
        width: auto;
        margin-left: 0 !important;
        margin-top: 0px !important;  /* Oberer Rand über dem Logo */

            
    }

    /* Sidebar-Header ausrichten */
    div[data-testid="stSidebarHeader"], div[data-testid="collapsedControl"] {
        display: flex;
        align-items: center;
        justify-content: flex-start;  /* Links ausrichten */
    }
    </style>
""", unsafe_allow_html=True)



# logo_path = Path(__file__).parent / "assets" / "logo.png"
# st.image(str(logo_path), width=120)

# --- Google Sheets ---
SHEET_ID = "1k3oiVYXVdRJJbK20KQY80zysN_pE9WzSt7QSIFx2h1w"

def load_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df = normalize_commas(df)
    return df

def normalize_commas(df):
    for col in df.columns:
        df[col] = df[col].apply(lambda x: float(str(x).replace(",", ".")) if isinstance(x, str) and re.match(r"^\d+,\d+$", x) else x)
    return df

if "df_cells" not in st.session_state:
    st.session_state.df_cells = load_sheet("Cells")
if "df_housing" not in st.session_state:
    st.session_state.df_housing = load_sheet("Housing")
if "df_electronics" not in st.session_state:
    st.session_state.df_electronics = load_sheet("Electronics")

# Dann überall im Code:
df_cell = st.session_state.df_cells
df_housing = st.session_state.df_housing
df_electronics = st.session_state.df_electronics

# --- Page Config ---
pages = {
    "general": "General Information",
    "cell": "Cell Configuration",
    "components": "Housing & Electronics",
    "reuse": "Reuse & Remanufacturing",
    "summary": "Battery Pass Preview"
}


st.set_page_config(page_title="Battery Pass Go", page_icon="🔋")

# Logo ganz oben einfügen
st.logo(
    "assets/logo.png",  # Pfad zu deinem Logo
    link="https://ohrenberg.eu",  # optionaler Link
    icon_image="assets/logo.png",        # optional für kleinere Darstellung z. B. im mobilen Menü
    size="large"
)

# --- Sidebar ---
#st.sidebar.title("Overview")
# Google Fonts einbinden
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,700;1,700&display=swap" rel="stylesheet">
    <style>
    .sidebar-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 900;
        font-size: 1.4rem;
        margin-bottom: 1rem;
    }
    .sidebar-title .go {
        color: #00CC2D;
        font-style: italic;
    }
    </style>
""", unsafe_allow_html=True)

# Überschrift in der Sidebar anzeigen
st.sidebar.title("ㅤ")
#st.sidebar.title("ㅤ")
st.sidebar.markdown('<div class="sidebar-title">Battery Pass <span class="go">GO</span></div>', unsafe_allow_html=True)



for key, label in pages.items():
    complete = st.session_state.get(f"{key}_complete", False)
    icon = "✅" if complete else "🔲"
    st.sidebar.markdown(f"{icon} {label}")

st.sidebar.markdown("---")
if st.sidebar.button("ㅤ🗑️ Reset all inputsㅤ"):
    preserved = ["current_page"]
    for key in list(st.session_state.keys()):
        if key not in preserved:
            del st.session_state[key]
    st.session_state["form_data"] = {}
    st.session_state.current_page = "general"
    st.rerun()

# --- State Init ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "general"
if "go_next" not in st.session_state:
    st.session_state.go_next = False
if "go_back" not in st.session_state:
    st.session_state.go_back = False
if "form_data" not in st.session_state:
    st.session_state.form_data = {}

# --- Navigation Logic ---
if st.session_state.get("go_next"):
    st.session_state.go_next = False
    keys = list(pages.keys())
    idx = keys.index(st.session_state.current_page)

    current = st.session_state.current_page
    if current == "general":
        st.session_state.form_data.update({
            "battery_category": st.session_state.get("battery_category"),
            "manufacturer_id": st.session_state.get("manufacturer_id"),
            "operator_id": st.session_state.get("operator_id"),
            "manufacturing_place": st.session_state.get("manufacturing_place"),
            "fire_extinguisher": st.session_state.get("fire_extinguisher"),
            "warranty_period": st.session_state.get("warranty_period"),
        })
    elif current == "cell":
        st.session_state.form_data.update({
            "cell_manufacturer": st.session_state.get("cell_manufacturer"),
            "cell_model": st.session_state.get("cell_model"),
            "series": st.session_state.get("series"),
            "parallel": st.session_state.get("parallel"),
        })
    elif current == "reuse":
        # Nur wenn alle anderen Seiten vollständig sind
        if st.session_state.get("general_complete") and st.session_state.get("cell_complete") and st.session_state.get("components_complete") and st.session_state.get("reuse_complete"):
            st.session_state["summary_complete"] = True

    if idx + 1 < len(keys):
        st.session_state.current_page = keys[idx + 1]
        st.rerun()

if st.session_state.get("go_back"):
    st.session_state.go_back = False
    keys = list(pages.keys())
    idx = keys.index(st.session_state.current_page)
    if idx - 1 >= 0:
        st.session_state.current_page = keys[idx - 1]
        st.rerun()

# --- Page Content ---
if st.session_state.current_page == "general":
    st.title("General Battery Information")

    options = ["EV", "Industrial", "LV"]
    st.selectbox("Battery category", options,
        index=options.index(st.session_state.form_data.get("battery_category", options[0])),
        key="battery_category")

    st.text_input("Manufacturer identification", st.session_state.form_data.get("manufacturer_id", ""), key="manufacturer_id")
    st.text_input("Economic operator identification", st.session_state.form_data.get("operator_id", ""), key="operator_id")
    st.text_input("Manufacturing place", st.session_state.form_data.get("manufacturing_place", ""), key="manufacturing_place")
    st.text_input("Appropriate fire extinguishing agents", st.session_state.form_data.get("fire_extinguisher", "Class D fire extinguishers"), key="fire_extinguisher")
    st.number_input("Calendar life warranty period (years)", min_value=0, step=1, value=st.session_state.form_data.get("warranty_period", 0), key="warranty_period")

    complete = all(st.session_state.get(k) not in (None, "", 0) for k in [
        "battery_category", "manufacturer_id", "operator_id", "manufacturing_place", "fire_extinguisher", "warranty_period"
    ])
    st.session_state["general_complete"] = complete

elif st.session_state.current_page == "cell":
    st.title("Cell Configuration")

    # Auswahl Hersteller und Modell
    manufacturers = sorted(df_cell["Manufacturer"].dropna().unique())
    default_manufacturer = st.session_state.form_data.get("cell_manufacturer", manufacturers[0])
    st.selectbox("Select manufacturer", manufacturers,
        index=manufacturers.index(default_manufacturer) if default_manufacturer in manufacturers else 0,
        key="cell_manufacturer")

    models = df_cell[df_cell["Manufacturer"] == st.session_state.cell_manufacturer]["Model"].dropna().unique()
    models_sorted = sorted(models)
    default_model = st.session_state.form_data.get("cell_model", models_sorted[0] if models_sorted else "")
    st.selectbox("Select cell model", models_sorted,
        index=models_sorted.index(default_model) if default_model in models_sorted else 0,
        key="cell_model")

    # Zellobjekt holen
    cell = df_cell[
        (df_cell["Manufacturer"] == st.session_state.cell_manufacturer) &
        (df_cell["Model"] == st.session_state.cell_model)
    ].iloc[0]

    # Eingabe: Anzahl in Reihe und Parallel
    col1, col2 = st.columns(2)
    s = col1.number_input("Number in series", min_value=1, step=1,
                          value=st.session_state.form_data.get("series", 1), key="series")
    p = col2.number_input("Number in parallel", min_value=1, step=1,
                          value=st.session_state.form_data.get("parallel", 1), key="parallel")

    total_cell = s * p

    # -----------------------------
    # [1] BERECHNUNGEN
    # -----------------------------
    energy_total = cell["Energy [Wh]"] * total_cell

    co2_materials_cell = cell["CO2 Materials [CO2eq kg]"] * total_cell
    co2_production_cell = cell["CO2 Cell Production [CO2eq kg]"] * total_cell
    co2_distribution_cell = cell["CO2 Distribution [CO2eq kg]"] * total_cell
    co2_recycling_cell = 0.0  # aktuell nicht in Datenbank, daher 0 annehmen

    co2_total_cell = co2_materials_cell + co2_production_cell + co2_distribution_cell
   
    # Prozentanteile berechnen
    co2_percent_materials_cell = (co2_materials_cell / co2_total_cell) * 100 if co2_total_cell > 0 else 0
    co2_percent_production_cell = (co2_production_cell / co2_total_cell) * 100 if co2_total_cell > 0 else 0
    co2_percent_distribution_cell = (co2_distribution_cell / co2_total_cell) * 100 if co2_total_cell > 0 else 0
    co2_percent_recycling_cell = (co2_recycling_cell / co2_total_cell) * 100 if co2_total_cell > 0 else 0

    cycles = cell["Expected number of charge-discharge cycles"]
    total_energy_fu = cell["Energy [Wh]"] * total_cell * cycles/1000
    co2_per_functional_unit_cell = co2_total_cell / total_energy_fu if total_energy_fu > 0 else 0
    
    nominal_voltage_pack = s * cell["Nominal Voltage [V]"]
    min_voltage_pack = s * cell["Min. Voltage [V]"]
    max_voltage_pack = s * cell["Max. Voltage [V]"]
    
    capacity_pack = cell["Nominal capacity [mAh]"] * p

    resistance_pack = cell["Internal resistance [Ω]"] * s / p

    power_continuous_pack = cell["Power continous [W]"] * p


    #Materials
    battery_chemistry = cell["Battery chemistry"]
    critical_raw_materials = cell["Critical raw materials"]
    hazardous_substances = cell["Hazardous substances"]
    anode_composition = cell["Anode Composition"]
    cathode_composition = cell["Cathode Composition"]
    electrolyte_composition = cell["Electrolyte Composition"]

    # -----------------------------
    # [2] SPEICHERN IN SESSION_STATE
    # -----------------------------
    st.session_state.form_data.update({
        "nominal_voltage_pack": nominal_voltage_pack,
        "min_voltage_pack": min_voltage_pack,
        "max_voltage_pack": max_voltage_pack,
        "capacity_pack": capacity_pack,
        "resistance_pack": resistance_pack,
        "power_continuous_pack": power_continuous_pack,
        "nominal_capacity": cell["Nominal capacity [mAh]"],
        "nominal_voltage": cell["Nominal Voltage [V]"],
        "min_voltage": cell["Min. Voltage [V]"],
        "max_voltage": cell["Max. Voltage [V]"],
        "original_power": cell["Power continous [W]"],
        "charge_discharge_cycles": cycles,
        "reference_test": cell["Reference cycle-life test"],
        "expected_lifetime": cell["Expected lifetime in calendar years"],
        "min_operating_temp": cell["Min. Temp. [°C]"],
        "max_operating_temp": cell["Max. Temp. [°C]"],
        "min_storage_temp": cell["Min. Temp. [°C]"],
        "max_storage_temp": cell["Max. Temp. [°C]"],
        "efficiency_initial": cell["Round trip energy efficiency (initial)"],
        "efficiency_midlife": cell["Round trip energy efficiency (50 % of cycle-life)"],
        "resistance_cell": cell["Internal resistance [Ω]"],
        "resistance_pack": resistance_pack,

        "cycles": cycles,
        "total_energy_fu": total_energy_fu,

        "battery_chemistry": battery_chemistry,
        "critical_raw_materials": critical_raw_materials,
        "hazardous_substances": hazardous_substances,
        "anode_composition": anode_composition,
        "cathode_composition": cathode_composition,
        "electrolyte_composition": electrolyte_composition,


        "recycled_share_li": cell.get("Recycled share for Lithium", 0),
        "recycled_share_ni": cell.get("Recycled share for Nickel", 0),
        "recycled_share_co": cell.get("Recycled share for Cobalt", 0),
        "recycled_share_pb": cell.get("Recycled share for Lead", 0),

        "battery_carbon_footprint": co2_per_functional_unit_cell,

        "energy_total": energy_total,
        "co2_total_cell": co2_total_cell,

        "co2_materials_cell": co2_materials_cell,
        "co2_production_cell": co2_production_cell,
        "co2_distribution_cell": co2_distribution_cell,
        "co2_recycling_cell": co2_recycling_cell
        


    })

    # -----------------------------
    # [3] ANZEIGE DER WERTE
    # -----------------------------
    st.markdown("---")
    st.subheader("Electrical Specifications")

    st.write(f"Total capacity (pack): **{capacity_pack:.0f} mAh**")
    st.write(f"Total energy content (pack): **{energy_total:.2f} Wh**")
    st.write(f"Nominal voltage (pack): **{nominal_voltage_pack:.2f} V**")
    st.write(f"Min voltage (pack): **{min_voltage_pack:.2f} V**")
    st.write(f"Max voltage (pack): **{max_voltage_pack:.2f} V**")
    st.write(f"Continuous power (pack): **{power_continuous_pack:.2f} W**")

    st.write(f"Expected charge-discharge cycles: **{cycles}**")
    st.write(f"Reference cycle-life test: **{cell['Reference cycle-life test']}**")
    st.write(f"Expected lifetime in calendar years: **{cell['Expected lifetime in calendar years']} years**")
    st.write(f"Min Operating Temperature: **{cell['Min. Temp. [°C]']} °C**")
    st.write(f"Max Operating Temperature: **{cell['Max. Temp. [°C]']} °C**")
    st.write(f"Min Storage Temperature: **{cell['Min. Temp. [°C]']} °C**")
    st.write(f"Max Storage Temperature: **{cell['Max. Temp. [°C]']} °C**")
    st.write(f"Round trip energy efficiency (initial): **{cell['Round trip energy efficiency (initial)']} %**")
    st.write(f"Round trip energy efficiency (50% life): **{cell['Round trip energy efficiency (50 % of cycle-life)']} %**")
    st.write(f"Internal cell resistance: **{cell['Internal resistance [Ω]']} Ω**")
    st.write(f"Internal pack resistance: **{resistance_pack} Ω**")

    st.markdown("---")
    st.subheader("Materials")
    st.write(f"battery_chemistry: **{battery_chemistry}**")
    st.write(f"critical_raw_materials: **{critical_raw_materials}**")
    st.write(f"hazardous_substances: **{hazardous_substances}**")
    st.write(f"anode_composition: **{anode_composition}**")
    st.write(f"cathode_composition: **{cathode_composition}**")
    st.write(f"electrolyte_composition: **{electrolyte_composition}**")

    st.markdown("---")
    st.subheader("Circularity")
    st.write(f"Recycled share for Lithium: **{cell.get('Recycled share for Lithium', 0)} %**")
    st.write(f"Recycled share for Nickel: **{cell.get('Recycled share for Nickel', 0)} %**")
    st.write(f"Recycled share for Cobalt: **{cell.get('Recycled share for Cobalt', 0)} %**")
    st.write(f"Recycled share for Lead: **{cell.get('Recycled share for Lead', 0)} %**")

    st.markdown("---")
    st.subheader("Carbon Footprint")
    st.write(f"Total CO₂ footprint (cell): **{co2_total_cell:.2f} kg CO₂eq**")
    st.write(f"Battery carbon footprint per Functional Unit: **{co2_per_functional_unit_cell:.4f} kg CO₂/kWh**")
    st.write(f"Carbon footprint class: *n/a*")
    st.write(f"Contribution raw material & housing: **{co2_percent_materials_cell:.2f} %**")
    st.write(f"Contribution production: **{co2_percent_production_cell:.2f} %**")
    st.write(f"Contribution distribution: **{co2_percent_distribution_cell:.2f} %**")
    st.write(f"Contribution end-of-life: **{co2_percent_recycling_cell:.2f} %**")


    st.session_state["cell_complete"] = all([
        st.session_state.get(k) for k in ["cell_manufacturer", "cell_model", "series", "parallel"]
    ])

elif st.session_state.current_page == "components":
    st.title("Housing & Electronics")

    # --- Eingabe: Housing-Materialien ---
    st.subheader("Add housing materials")
    housing_materials = []

    if "housing_counter" not in st.session_state:
        st.session_state.housing_counter = 1

    for i in range(st.session_state.housing_counter):
        cols = st.columns([2, 1])
        material = cols[0].selectbox(" ", df_housing["Material"].unique(), key=f"material_{i}")
        weight = cols[1].number_input(
            "Weight in g", min_value=0, step=1, format="%d",
            value=st.session_state.form_data.get(f"weight_{i}", 100), key=f"weight_{i}"
        )
        st.session_state.form_data[f"material_{i}"] = material
        st.session_state.form_data[f"weight_{i}"] = weight
        housing_materials.append((material, weight))

    if st.button("Add another housing material"):
        st.session_state.housing_counter += 1
        st.rerun()

    st.divider()

    # --- Eingabe: Elektronik-Komponenten ---
    st.subheader("Add electronic components")
    electronic_materials = []

    if "electronics_counter" not in st.session_state:
        st.session_state.electronics_counter = 1

    for i in range(st.session_state.electronics_counter):
        cols = st.columns([2, 1])
        material = cols[0].selectbox(" ", df_electronics["Material"].unique(), key=f"electronics_material_{i}")
        weight = cols[1].number_input(
            "Weight in g", min_value=0, step=1, format="%d",
            value=st.session_state.form_data.get(f"electronics_weight_{i}", 50), key=f"electronics_weight_{i}"
        )
        st.session_state.form_data[f"electronics_material_{i}"] = material
        st.session_state.form_data[f"electronics_weight_{i}"] = weight
        electronic_materials.append((material, weight))

    if st.button("Add another component"):
        st.session_state.electronics_counter += 1
        st.rerun()

    # --- [1] BERECHNUNG ---
    co2_housing = sum([
        (weight / 1000) * df_housing.set_index("Material").loc[material, "CO2 [CO2eq kg/kg]"]
        for material, weight in housing_materials
    ])

    co2_electronics = sum([
        (weight / 1000) * df_electronics.set_index("Material").loc[material, "CO2 [CO2eq kg/kg]"]
        for material, weight in electronic_materials
    ])

    # --- [2] UPDATE: Session-State ---
    st.session_state.form_data["co2_housing"] = co2_housing
    st.session_state.form_data["co2_electronics"] = co2_electronics
    st.session_state["components_complete"] = (
        len(housing_materials) > 0 and len(electronic_materials) > 0
    )

    # --- [3] ANZEIGE: CO₂-Ergebnisse ---
    st.markdown("---")
    st.subheader("Carbon Footprint")

    st.markdown(f"Housing Materials: **{co2_housing:.2f} kg CO₂eq**")
    st.markdown(f"Electronic Components: **{co2_electronics:.2f} kg CO₂eq**")


elif st.session_state.current_page == "reuse":
    st.title("Reuse & Remanufacturing")

    # -----------------------------
    # [1] EINGABEFELDER
    # -----------------------------
    st.text_input(
        "Spare part supplier",
        value=st.session_state.form_data.get("spare_part_supplier", ""),
        key="spare_part_supplier"
    )
    st.text_input(
        "Postal address",
        value=st.session_state.form_data.get("postal_address", ""),
        key="postal_address"
    )
    st.text_input(
        "E-Mail",
        value=st.session_state.form_data.get("email", ""),
        key="email"
    )
    st.text_input(
        "Web address",
        value=st.session_state.form_data.get("web_address", ""),
        key="web_address"
    )
    st.text_input(
        "Component part numbers",
        value=st.session_state.form_data.get("component_part_numbers", ""),
        key="component_part_numbers"
    )

    # -----------------------------
    # [2] SESSION-STATE UPDATE
    # -----------------------------
    text_fields = [
        "spare_part_supplier",
        "postal_address",
        "email",
        "web_address",
        "component_part_numbers",
    ]

    for key in text_fields:
        st.session_state.form_data[key] = st.session_state.get(key, "")

    # -----------------------------
    # [3] ABSCHLUSS-CHECK
    # -----------------------------
    complete = all(st.session_state.get(k) not in (None, "", 0) for k in [
        "spare_part_supplier", "postal_address", "email", "web_address", "component_part_numbers"
    ])
    st.session_state["reuse_complete"] = complete


elif st.session_state.current_page == "summary":

    st.title("Battery Passport Summary")
    form_data = st.session_state.get("form_data", {})

    # Dann die numerischen Felder normalisieren:
    numeric_fields = {
        "capacity_pack": float,
        "weight": float,
        "warranty_period": int,
        "nominal_voltage_pack": float,
        "min_voltage_pack": float,
        "max_voltage_pack": float,
        "power_continuous_pack": float,
        "resistance_cell": float,
        "resistance_pack": float,
        "charge_discharge_cycles": int,
        "expected_lifetime": int,
        "min_operating_temp": float,
        "max_operating_temp": float,
        "min_storage_temp": float,
        "max_storage_temp": float,
        "efficiency_initial": float,
        "efficiency_midlife": float,
        "recycled_share_li": float,
        "recycled_share_ni": float,
        "recycled_share_co": float,
        "recycled_share_pb": float,
        "co2_total": float,
        "co2_per_fu": float,
        "co2_material_pack_precentage": float,
        "co2_production_pack_precentage": float,
        "co2_distribution_pack_precentage": float,
        "co2_recycling_pack_precentage": float
    }

    for key, cast_fn in numeric_fields.items():
        val = form_data.get(key)
        if isinstance(val, str):
            try:
                form_data[key] = cast_fn(val.replace(",", "."))
            except Exception:
                pass

    # -----------------------------
    # [1] BERECHNUNGEN
    # -----------------------------
    # CO₂ absolute Werte aus form_data
    co2_total_cell = form_data.get("co2_total_cell", 0)

    co2_materials_cell = form_data.get("co2_materials_cell", 0)
    co2_production_cell = form_data.get("co2_production_cell", 0)
    co2_distribution_cell = form_data.get("co2_distribution_cell", 0)
    co2_recycling_cell = form_data.get("co2_recycling_cell", 0)

    co2_housing = form_data.get("co2_housing", 0)
    co2_electronics = form_data.get("co2_electronics", 0)
    
    co2_material_pack = co2_materials_cell + co2_housing + co2_electronics
    co2_total_pack = co2_material_pack + co2_production_cell + co2_distribution_cell + co2_recycling_cell

    co2_percent_materials_pack = (co2_material_pack / co2_total_pack * 100) if co2_total_pack > 0 else 0
    co2_percent_production_pack = (co2_production_cell / co2_total_pack * 100) if co2_total_pack > 0 else 0
    co2_percent_distribution_pack = (co2_distribution_cell / co2_total_pack * 100) if co2_total_pack > 0 else 0
    co2_percent_recycling_pack = (co2_recycling_cell / co2_total_pack * 100) if co2_total_pack > 0 else 0

    cycles = form_data.get("cycles", 0)
    total_energy_fu = form_data.get("total_energy_fu", 0)
    co2_per_functional_unit_pack = co2_total_pack / total_energy_fu if total_energy_fu > 0 else 0

    # Gewicht schätzen
    cell_mass = df_cell[
        (df_cell["Manufacturer"] == form_data.get("cell_manufacturer")) &
        (df_cell["Model"] == form_data.get("cell_model"))
    ]["Mass [g]"].values[0]
    total_cell = form_data.get("series", 1) * form_data.get("parallel", 1)
    weight_cell = cell_mass * total_cell
    weight_housing = sum([form_data.get(k, 0) for k in form_data if k.startswith("weight_")])
    weight_electronics = sum([form_data.get(k, 0) for k in form_data if k.startswith("electronics_weight_")])
    total_weight = (weight_cell + weight_housing + weight_electronics)/1000

    # -----------------------------
    # [2] SESSION UPDATE
    # -----------------------------
    form_data.update({
        "weight": round(total_weight, 1),
        "co2_total_pack": round(co2_total_pack, 2),
        "co2_percent_materials_pack": round(co2_percent_materials_pack, 2),
        "co2_percent_production_pack": round(co2_percent_production_pack, 2),
        "co2_percent_distribution_pack": round(co2_percent_distribution_pack, 2),
        "co2_percent_recycling_pack": round(co2_percent_recycling_pack, 2),
        "co2_per_functional_unit_pack": round(co2_per_functional_unit_pack, 2)
    })

    # -----------------------------
    # [3] ANZEIGE
    # -----------------------------
    st.markdown("---")
    st.subheader("General Battery Information")
    st.write(f"Battery category: **{form_data.get('battery_category', 'n/a')}**")
    st.write(f"Manufacturer identification: **{form_data.get('manufacturer_id', 'n/a')}**")
    st.write(f"Economic operator identification: **{form_data.get('operator_id', 'n/a')}**")
    st.write(f"Manufacturing place: **{form_data.get('manufacturing_place', 'n/a')}**")
    
    st.write(f"Weight: **{form_data.get('weight', 'n/a')} kg**")
    st.write(f"Appropriate fire extinguishing agents: **{form_data.get('fire_extinguisher', 'n/a')}**")
    st.write(f"Calendar life warranty period: **{form_data.get('warranty_period', 'n/a')} years**")

    st.markdown("---")
    st.subheader("Electrical Specifications")
    st.write(f"Capacity (pack): **{form_data.get('capacity_pack', 'n/a')} mAh**")
    st.write(f"Total energy content (pack): **{form_data.get('energy_total', 'n/a')} Wh**")
    st.write(f"Nominal voltage (pack): **{form_data.get('nominal_voltage_pack', 'n/a')} V**")
    st.write(f"Minimum voltage (pack): **{form_data.get('min_voltage_pack', 'n/a')} V**")
    st.write(f"Maximum voltage (pack): **{form_data.get('max_voltage_pack', 'n/a')} V**")
    st.write(f"Continuous power (pack): **{form_data.get('power_continuous_pack', 'n/a')} W**")
    st.write(f"Internal resistance (cell): **{form_data.get('resistance_cell', 'n/a')} Ω**")
    st.write(f"Internal resistance (pack): **{form_data.get('resistance_pack', 'n/a')} Ω**")
    st.write(f"Expected number of charge-discharge cycles: **{form_data.get('charge_discharge_cycles', 'n/a')} cycles**")
    st.write(f"Reference cycle-life test: **{form_data.get('reference_test', 'n/a')}**")
    st.write(f"Expected lifetime: **{form_data.get('expected_lifetime', 'n/a')} years**")
    st.write(f"Min Operating temperature: **{form_data.get('min_operating_temp', 'n/a')} °C**")
    st.write(f"Max Operating temperature: **{form_data.get('max_operating_temp', 'n/a')} °C**")
    st.write(f"Min Storage temperature: **{form_data.get('min_storage_temp', 'n/a')} °C**")
    st.write(f"Max Storage temperature: **{form_data.get('max_storage_temp', 'n/a')} °C**")
    st.write(f"Round trip efficiency (initial): **{form_data.get('efficiency_initial', 'n/a')} %**")
    st.write(f"Round trip efficiency (50% life): **{form_data.get('efficiency_midlife', 'n/a')} %**")

    st.markdown("---")
    st.subheader("Circularity")
    st.write(f"Recycled share for Lithium: **{form_data.get('recycled_share_li', 0)} %**")
    st.write(f"Recycled share for Nickel: **{form_data.get('recycled_share_ni', 0)} %**")
    st.write(f"Recycled share for Cobalt: **{form_data.get('recycled_share_co', 0)} %**")
    st.write(f"Recycled share for Lead: **{form_data.get('recycled_share_pb', 0)} %**")

    st.markdown("---")
    st.subheader("Carbon Footprint")
    st.write(f"Total CO₂ footprint (pack): **{form_data.get('co2_total_pack', 'n/a')} kg CO₂eq**")
    st.write(f"Battery carbon footprint per Functional Unit: **{form_data.get('co2_per_functional_unit_pack', 'n/a')} kg CO₂/kWh**")
    st.write(f"Carbon footprint performance class: *n/a*")
    st.write(f"Contribution raw material & housing: **{form_data.get('co2_percent_materials_pack', 'n/a')} %**")
    st.write(f"Contribution production: **{form_data.get('co2_percent_production_pack', 'n/a')} %**")
    st.write(f"Contribution distribution: **{form_data.get('co2_percent_distribution_pack', 'n/a')} %**")
    st.write(f"Contribution end-of-life and recycling: **{form_data.get('co2_percent_recycling_pack', 'n/a')} %**")

    st.markdown("---")
    st.subheader("Reuse & Remanufacturing")
    st.write(f"Spare part supplier: **{form_data.get('spare_part_supplier', 'n/a')}**")
    st.write(f"Postal address: **{form_data.get('postal_address', 'n/a')}**")
    st.write(f"E-Mail: **{form_data.get('email', 'n/a')}**")
    st.write(f"Web address: **{form_data.get('web_address', 'n/a')}**")
    st.write(f"Component part numbers: **{form_data.get('component_part_numbers', 'n/a')}**")
    
    st.markdown("---")

    # Schritt 1: API-Key eingeben
    api_token = st.text_input("🔑 Enter your open-dpp API token", type="password")

    # Schritt 2: Button nur anzeigen, wenn API-Key vorhanden ist
    if api_token:
        if st.button("✅ Create Battery Passport @ open-dpp"):
            create_model_and_upload_data(form_data, api_token)
    else:
        st.info("Please enter your API token to proceed.")
    


# --- Navigation ---
st.markdown("---")
col_back, col_next, col_spacer = st.columns([1, 1, 3])

with col_back:
    if st.button("ㅤㅤ**Back**ㅤㅤ", disabled=st.session_state.current_page == "general"):
        st.session_state.go_back = True
        st.rerun()

with col_next:
    if st.button("ㅤㅤ**Next**ㅤㅤ", disabled=st.session_state.current_page == list(pages)[-1]):
        st.session_state.go_next = True
        st.rerun()










