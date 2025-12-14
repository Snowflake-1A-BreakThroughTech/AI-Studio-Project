import streamlit as st
import pandas as pd
import pydeck as pdk
import json
from shapely import wkb

from snowflake.snowpark.context import get_active_session
session = get_active_session()
st.set_page_config(layout="wide")

#------------------------------------------------------------------------>
# Get ZIP CODES
query = """
SELECT *
FROM BROOKLYN_DATA.DATA.ZIPCODE_LABELS;
"""
zipcodes = session.sql(query).to_pandas()

#------------------------------------------------------------------------>
# Get AMENITIES DATA
amenities_query = """
SELECT C3, C4, C5, C6
FROM BROOKLYN_DATA.OSM.TRANSPORTATION;
"""
amenities_df = session.sql(amenities_query).to_pandas()
amenities_df.columns = amenities_df.iloc[0]
amenities_df = amenities_df[1:].reset_index(drop=True)

amenities_df['LAT'] = pd.to_numeric(amenities_df['LAT'], errors='coerce')
amenities_df['LON'] = pd.to_numeric(amenities_df['LON'], errors='coerce')
amenities_df['ZIPCODE'] = amenities_df['ZIPCODE'].astype(str)

#------------------------------------------------------------------------>
# -----------------------------
# MODEL SELECTION SLIDER
# -----------------------------
st.title("Brooklyn Transport Demand Prediction Dashboard")

st.subheader("Predicted Demand by Population Increase")
model_pct = st.slider(
    "Select Population Increase (%)",
    min_value=0,
    max_value=25,
    step=5,
    value=10
)
st.info("💡 Darker purple areas show lower demand, while yellow areas show higher predicted transport demand.")

table_name = f"DEMAND_SCORES_{model_pct}PCT"

zipcodes["ZIPCODE"] = zipcodes["ZIPCODE"].astype(str)

# -----------------------------
# DEMAND SCORES
# -----------------------------
demand_scores = session.table(f"BROOKLYN_DATA.PREDICTIONS.{table_name}").to_pandas()

demand_scores.columns = ["DEMAND_SCORE"]
demand_scores["DEMAND_SCORE"] = demand_scores["DEMAND_SCORE"].astype(float)

demand_df = pd.concat([zipcodes, demand_scores], axis=1)
demand_df["ZIPCODE"] = demand_df["ZIPCODE"].astype(str)

amenities_df['tooltip'] = amenities_df.apply(
    lambda row: f"""
    <div style="
        background-color: rgba(255, 255, 255, 0.95);
        padding: 8px 12px;
        border-radius: 6px;
        color: black;
        font-family: 'Arial';
        font-size: 13px;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
    ">
        <b>Amenity:</b> {row['AMENITY']}<br>
        <b>ZIP Code:</b> {row['ZIPCODE']}<br>
    </div>
    """, 
    axis=1
)

query = """
SELECT VARIANT_COL
FROM BROOKLYN_DATA.OSM.ZIPCODE_POLYGONS
"""

geo_row = session.sql(query).to_pandas().iloc[0,0]
geojson_full = json.loads(geo_row) if isinstance(geo_row, str) else geo_row

brooklyn_features = [
    f for f in geojson_full["features"]
    if f["properties"].get("borough") == "Brooklyn" and f["properties"].get("postalCode") != '11693'
]

brooklyn_geojson = {
    "type": "FeatureCollection",
    "features": brooklyn_features
}

#--------------------------------------------------------------------------->

view_state = pdk.ViewState(
    latitude=40.65,
    longitude=-73.95,
    zoom=10.5
)

demand_features = []
for feature in brooklyn_features:
    postal = feature["properties"].get("postalCode", None)
    feature_copy = feature.copy()
    if postal and postal in demand_df["ZIPCODE"].values:
        score = demand_df.loc[demand_df["ZIPCODE"] == postal, "DEMAND_SCORE"].iloc[0]
        score = float(f"{score:.2g}") 
        feature_copy["properties"]["demand_score"] = score
        # Add tooltip to properties
        feature_copy["properties"]["tooltip"] = f"""
        <div style="
            background-color: rgba(255, 255, 255, 0.95);
            padding: 8px 12px;
            border-radius: 6px;
            color: black;
            font-family: 'Arial';
            font-size: 13px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
            <b>ZIP Code:</b> {postal}<br>
            <b>Demand:</b> {score}
        </div>
        """
        if score < 0.25:
            t = score * 4
            color = [int(68 + (59-68)*t), int(1 + (82-1)*t), int(84 + (139-84)*t), 180]
        elif score < 0.5:
            t = (score - 0.25) * 4
            color = [int(59 + (33-59)*t), int(82 + (144-82)*t), int(139 + (140-139)*t), 180]
        elif score < 0.75:
            t = (score - 0.5) * 4
            color = [int(33 + (94-33)*t), int(144 + (201-144)*t), int(140 + (98-140)*t), 180]
        else:
            t = (score - 0.75) * 4
            color = [int(94 + (253-94)*t), int(201 + (231-201)*t), int(98 + (37-98)*t), 180] 
    else:
        feature_copy["properties"]["demand_score"] = None
        feature_copy["properties"]["tooltip"] = f"""
        <div style="
            background-color: rgba(255, 255, 255, 0.95);
            padding: 8px 12px;
            border-radius: 6px;
            color: black;
            font-family: 'Arial';
            font-size: 13px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        ">
            <b>ZIP Code:</b> {postal}<br>
            <b>Demand:</b> N/A
        </div>
        """
        color = [200, 200, 200, 50]  
    feature_copy["properties"]["fill_color"] = color
    demand_features.append(feature_copy)

demand_layer = pdk.Layer(
    "GeoJsonLayer",
    data={
        "type": "FeatureCollection",
        "features": demand_features
    },
    stroked=True,
    filled=True,
    pickable=True,
    auto_highlight=True,
    get_fill_color="properties.fill_color",
    get_line_color=[0, 0, 0],
    get_line_width=30,
)

# -----------------------------
# AMENITIES LAYER
# -----------------------------
amenity_colors = {
    'parking': [255, 69, 0, 255],  # Red-Orange
    'bicycle_parking': [0, 191, 255, 255],  # Deep Sky Blue
    'parking_entrance': [139, 0, 139, 255],  # Dark Magenta
    'fuel': [255, 215, 0, 255],  # Gold
    'bicycle_rental': [0, 255, 127, 255],  # Spring Green
    'charging_station': [138, 43, 226, 255],  # Blue Violet
    'car_wash': [0, 255, 255, 255],  # Cyan
    'parking_space': [255, 20, 147, 255],  # Deep Pink
    'taxi': [255, 255, 0, 255],  # Yellow
    'car_rental': [178, 34, 34, 255],  # Firebrick Red
    'bicycle_repair_station': [124, 252, 0, 255],  # Lawn Green
    'car_sharing': [255, 0, 255, 255],  # Magenta
    'bus_station': [255, 140, 0, 255],  # Dark Orange
}

#-----------------------------------------------
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(
        """
        <style>
        .map-container {
            position: relative;
        }
        .map-legend {
            position: absolute;
            top: 100px; 
            right: 10px;
            background: rgba(255,255,255,0.9);
            padding: 10px 14px;
            border-radius: 8px;
            z-index: 9999;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
            font-size: 13px;
            max-height: 500px;
            overflow-y: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    show_amenities = st.checkbox("Show Transportation Amenities", value=False)
    
    if show_amenities:
        amenity_types = sorted(amenities_df['AMENITY'].unique().tolist())
        selected_amenities = st.multiselect(
            "Filter Amenity Types",
            options=amenity_types,
            default=amenity_types
        )
        filtered_amenities = amenities_df[amenities_df['AMENITY'].isin(selected_amenities)]
    else:
        filtered_amenities = pd.DataFrame()
    
    st.markdown('<div class="map-container">', unsafe_allow_html=True)
    
    if show_amenities:
        st.markdown(
            """
            <div class="map-legend">
                <b>Demand Legend</b><br>
                <div style="display:flex;align-items:center;margin-top:5px;">
                    <div style="width:20px;height:10px;background:rgb(68,1,84);margin-right:8px"></div>
                    Very Low
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="width:20px;height:10px;background:rgb(59,82,139);margin-right:8px"></div>
                    Low
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="width:20px;height:10px;background:rgb(33,144,140);margin-right:8px"></div>
                    Medium
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="width:20px;height:10px;background:rgb(94,201,98);margin-right:8px"></div>
                    High
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="width:20px;height:10px;background:rgb(253,231,37);margin-right:8px"></div>
                    Very High
                </div>
                <b style="margin-top:10px;display:block;">Amenities</b>
                <div style="display:flex;align-items:center;margin-top:5px;">
                    <div style="width:10px;height:10px;border-radius:50%;background:rgb(255,69,0);margin-right:8px"></div>
                    <span style="font-size:11px;">Parking</span>
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="width:10px;height:10px;border-radius:50%;background:rgb(0,191,255);margin-right:8px"></div>
                    <span style="font-size:11px;">Bike Parking</span>
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="width:10px;height:10px;border-radius:50%;background:rgb(139,0,139);margin-right:8px"></div>
                    <span style="font-size:11px;">Parking Entrance</span>
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="width:10px;height:10px;border-radius:50%;background:rgb(255,215,0);margin-right:8px"></div>
                    <span style="font-size:11px;">Fuel</span>
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="width:10px;height:10px;border-radius:50%;background:rgb(0,255,127);margin-right:8px"></div>
                    <span style="font-size:11px;">Bike Rental</span>
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="width:10px;height:10px;border-radius:50%;background:rgb(138,43,226);margin-right:8px"></div>
                    <span style="font-size:11px;">Charging Station</span>
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="width:10px;height:10px;border-radius:50%;background:rgb(0,255,255);margin-right:8px"></div>
                    <span style="font-size:11px;">Car Wash</span>
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="width:10px;height:10px;border-radius:50%;background:rgb(255,20,147);margin-right:8px"></div>
                    <span style="font-size:11px;">Parking Space</span>
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="width:10px;height:10px;border-radius:50%;background:rgb(255,255,0);margin-right:8px"></div>
                    <span style="font-size:11px;">Taxi</span>
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="width:10px;height:10px;border-radius:50%;background:rgb(178,34,34);margin-right:8px"></div>
                    <span style="font-size:11px;">Car Rental</span>
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="width:10px;height:10px;border-radius:50%;background:rgb(124,252,0);margin-right:8px"></div>
                    <span style="font-size:11px;">Bike Repair</span>
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="width:10px;height:10px;border-radius:50%;background:rgb(255,0,255);margin-right:8px"></div>
                    <span style="font-size:11px;">Car Sharing</span>
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="width:10px;height:10px;border-radius:50%;background:rgb(255,140,0);margin-right:8px"></div>
                    <span style="font-size:11px;">Bus Station</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="map-legend">
                <b>Demand Legend</b><br>
                <div style="display:flex;align-items:center;margin-top:5px;">
                    <div style="width:20px;height:10px;background:rgb(68,1,84);margin-right:8px"></div>
                    Very Low
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="width:20px;height:10px;background:rgb(59,82,139);margin-right:8px"></div>
                    Low
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="width:20px;height:10px;background:rgb(33,144,140);margin-right:8px"></div>
                    Medium
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="width:20px;height:10px;background:rgb(94,201,98);margin-right:8px"></div>
                    High
                </div>
                <div style="display:flex;align-items:center;">
                    <div style="width:20px;height:10px;background:rgb(253,231,37);margin-right:8px"></div>
                    Very High
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    if show_amenities and len(filtered_amenities) > 0:
        filtered_amenities_with_color = filtered_amenities.copy()
        filtered_amenities_with_color['color'] = filtered_amenities_with_color['AMENITY'].map(
            lambda x: amenity_colors.get(x, [128, 128, 128, 200])
        )
        
        amenities_layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered_amenities_with_color,
            get_position=['LON', 'LAT'],
            get_color='color',
            get_radius=30,
            pickable=True,
            auto_highlight=True,
            radius_min_pixels=3,
            radius_max_pixels=5,
        )
        
        display_deck = pdk.Deck(
            layers=[demand_layer, amenities_layer],
            initial_view_state=view_state,
            map_style='road',
            tooltip={"html": "{tooltip}",
                    "style": {"backgroundColor": "transparent"}}
        )
    else:
        display_deck = pdk.Deck(
            layers=[demand_layer],
            initial_view_state=view_state,
            map_style='road',
            tooltip={"html": "{tooltip}",
                    "style": {"backgroundColor": "transparent"}}
        )
    
    st.pydeck_chart(display_deck)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown(
        """
        <style>
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
            justify-content: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    data_table = f"TRANSPORT_DATA_{model_pct}PCT"
    df = session.sql(f'SELECT * FROM BROOKLYN_DATA.DATA."{data_table}"').to_pandas()
    
    df.insert(0, "DEMAND_SCORE", demand_df["DEMAND_SCORE"].values)
    
    df.index = zipcodes["ZIPCODE"].values
    df.index.name = "ZIPCODE"
    
    st.dataframe(df, height=600)