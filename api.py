import requests
import streamlit as st
import json

def create_model_and_upload_data(form_data, api_token):
    # --- Konfiguration ---
    api_token = api_token
    base_url = "https://api.cloud.open-dpp.de"
    organization_id = "2aeb51ad-5bd8-4769-a0f6-e18c7a8e9f11"
    template_id = "8f3bc7f4-337b-46bb-a8fc-fc9a32444a86"

    headers = {
        "Api_token": api_token,
        "Content-Type": "application/json"
    }
    # --- Schritt 1: Modell anlegen ---
    model_payload = {
        "name": f"{form_data.get('manufacturer_id', 'Unnamed Battery')}- {form_data.get('cell_model', '')}- {form_data.get('nominal_voltage_pack', '')}V- {form_data.get('capacity_pack', '')}mAh",
        "description": f"{form_data.get('battery_category', 'Battery')} - {form_data.get('cell_model', '')}",
        "templateId": template_id
    }

    response_model = requests.post(
        f"{base_url}/organizations/{organization_id}/models",
        headers=headers,
        json=model_payload
    )
    
    if response_model.status_code != 201:
        st.error("❌ Model creation failed.")
        return

    model_id = response_model.json().get("id")
    response_data = response_model.json()
    uuid = response_data.get("uniqueProductIdentifiers", [{}])[0].get("uuid")
    st.success(f"✅ Model created with ID: {model_id}")

    # --- Schritt 2: Daten vorbereiten und hochladen ---
    values = prepare_data_values(form_data)

    api_token = "39877680-38b9-4bc5-88f9-1776b5d856eb"
    base_url = "https://api.cloud.open-dpp.de"
    organization_id = "2aeb51ad-5bd8-4769-a0f6-e18c7a8e9f11"  # ggf. dynamisch
    url = f"{base_url}/organizations/{organization_id}/models/{model_id}/data-values"

    headers = {
        "Api_token": api_token,
        "Content-Type": "application/json"
    }

    # POST request
    response_values = requests.patch(
        url,
        headers=headers,
        json=values
    )

    # Erfolg oder Fehler
    if response_values.status_code == 200:
        st.success("✅ Battery pass data successfully uploaded.")
        view_url = f"https://view.cloud.open-dpp.de/{uuid}"

        st.markdown(
            f"""
            <div style="background-color:#d4edda;padding:16px;border-radius:8px;border:1px solid #c3e6cb;">
                <a href="{view_url}" target="_blank" style="text-decoration:none;font-weight:bold;color:#155724;">
                    🔗 View battery pass online
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error("❌ Failed to upload data values.")
        st.write("Status Code:", response_values.status_code)
        st.write("Response:", response_values.text)

def prepare_data_values(form_data):
    return [
        # General Information
        {"value": form_data.get("battery_category", "-"), "dataSectionId": "45822c0e-3568-43ac-a893-393d64da43df", "dataFieldId": "864a1f1d-4f0c-438d-becf-86a7b457ff6b", "row": 0},
        {"value": form_data.get("manufacturer_id", "-"), "dataSectionId": "45822c0e-3568-43ac-a893-393d64da43df", "dataFieldId": "ddebc1ea-d54d-451e-b484-bff44f2e7c6c", "row": 0},
        {"value": form_data.get("operator_id", "-"), "dataSectionId": "45822c0e-3568-43ac-a893-393d64da43df", "dataFieldId": "44674100-3472-4e1e-b8e2-a612bb074d25", "row": 0},
        {"value": form_data.get("manufacturing_place", "-"), "dataSectionId": "45822c0e-3568-43ac-a893-393d64da43df", "dataFieldId": "4e46c70b-1a91-475d-9cbd-70e6fa50ceec", "row": 0},
        {"value": f"{form_data.get('energy_total', 0):.0f} Wh", "dataSectionId": "45822c0e-3568-43ac-a893-393d64da43df", "dataFieldId": "7d9e8cde-1ad8-4065-bcbc-6b3004dcd435", "row": 0},
        {"value": f"{form_data.get('weight', 0):.1f} kg", "dataSectionId": "45822c0e-3568-43ac-a893-393d64da43df", "dataFieldId": "08846ed9-f31c-461b-ba21-7cf37a12aeff", "row": 0},
        {"value": form_data.get("fire_extinguisher", "-"), "dataSectionId": "45822c0e-3568-43ac-a893-393d64da43df", "dataFieldId": "37d985b6-8f3e-4a9d-a9d8-aab3c3de9e16", "row": 0},
        {"value": f"{form_data.get('warranty_period', 0)} years", "dataSectionId": "45822c0e-3568-43ac-a893-393d64da43df", "dataFieldId": "b5d8337e-6a9c-4b77-aeeb-84efd97a72c9", "row": 0},

        # Cell Chemistry
        {"value": "LiFePO4", "dataSectionId": "8fb09db8-c8b9-4d6e-8382-ef703046f1fe", "dataFieldId": "ceab99fa-92fc-4c2f-bb8b-099a560ceccc", "row": 0},
        {"value": "Lithium", "dataSectionId": "8fb09db8-c8b9-4d6e-8382-ef703046f1fe", "dataFieldId": "94b8e4ea-313a-4bc4-90bf-fd52c4079ffb", "row": 0},
        {"value": "LiPF6", "dataSectionId": "8fb09db8-c8b9-4d6e-8382-ef703046f1fe", "dataFieldId": "558c824c-b873-4693-9a84-273e190ffff5", "row": 0},
        {"value": "May cause fire or explosion; harmful to fertility and unborn child. Irritates eyes, skin, and respiratory system; Dangerous to the environment; Highly flammable", "dataSectionId": "8fb09db8-c8b9-4d6e-8382-ef703046f1fe", "dataFieldId": "cc8a8be5-46c8-40d6-a876-729a9b670e61", "row": 0},

        # Electrical Specifications
        {"value": f"{form_data.get('capacity_pack', 0) / 1000:.0f} Ah", "dataSectionId": "2bbd2ad2-3727-4a65-a646-3a8d565a9803", "dataFieldId": "9937a12f-1ec6-4f90-b467-43deb8636c93", "row": 0},
        {"value": f"{form_data.get('nominal_voltage_pack', 0):.1f} V", "dataSectionId": "2bbd2ad2-3727-4a65-a646-3a8d565a9803", "dataFieldId": "da40de8a-3795-4efb-b1b4-f60651791213", "row": 0},
        {"value": f"{form_data.get('min_voltage_pack', 0):.1f} V", "dataSectionId": "2bbd2ad2-3727-4a65-a646-3a8d565a9803", "dataFieldId": "fed4381b-a465-47e8-aa9c-cff33150b71b", "row": 0},
        {"value": f"{form_data.get('max_voltage_pack', 0):.1f} V", "dataSectionId": "2bbd2ad2-3727-4a65-a646-3a8d565a9803", "dataFieldId": "821561f5-e069-4858-bc6f-fdd20efcf4e5", "row": 0},
        {"value": f"{form_data.get('power_continuous_pack', 0) / 1000:.1f} kW", "dataSectionId": "2bbd2ad2-3727-4a65-a646-3a8d565a9803", "dataFieldId": "04e75b0a-970d-46eb-9215-f7759428ce70", "row": 0},
        {"value": str(form_data.get("charge_discharge_cycles", "-")), "dataSectionId": "2bbd2ad2-3727-4a65-a646-3a8d565a9803", "dataFieldId": "50e0ab0d-c211-4686-b547-333a0aba3ce1", "row": 0},
        {"value": form_data.get("reference_test", "-"), "dataSectionId": "2bbd2ad2-3727-4a65-a646-3a8d565a9803", "dataFieldId": "98eb3709-34c2-402d-b8bf-1a39cc07ec0f", "row": 0},
        {"value": f"{form_data.get('expected_lifetime', 0)} years", "dataSectionId": "2bbd2ad2-3727-4a65-a646-3a8d565a9803", "dataFieldId": "dc1488e7-3ba4-46ec-9300-549b34487374", "row": 0},
        {"value": f"{form_data.get('min_operating_temp', 0)} °C", "dataSectionId": "2bbd2ad2-3727-4a65-a646-3a8d565a9803", "dataFieldId": "ac209c45-6791-425e-ae31-d899833ffb4f", "row": 0},
        {"value": f"{form_data.get('max_operating_temp', 0)} °C", "dataSectionId": "2bbd2ad2-3727-4a65-a646-3a8d565a9803", "dataFieldId": "96298aab-6bff-42f3-80cd-4cf6f23c13a4", "row": 0},
        {"value": f"{form_data.get('min_storage_temp', 0)} °C", "dataSectionId": "2bbd2ad2-3727-4a65-a646-3a8d565a9803", "dataFieldId": "9b9349a0-6961-4810-88fb-a8e0c1483f27", "row": 0},
        {"value": f"{form_data.get('max_storage_temp', 0)} °C", "dataSectionId": "2bbd2ad2-3727-4a65-a646-3a8d565a9803", "dataFieldId": "fe90c834-0e13-4b03-a2bf-9b29a3f771b3", "row": 0},
        {"value": f"{form_data.get('efficiency_initial', 0)} %", "dataSectionId": "2bbd2ad2-3727-4a65-a646-3a8d565a9803", "dataFieldId": "06e2dc75-5895-437e-b76d-1090283f220f", "row": 0},
        {"value": f"{form_data.get('efficiency_midlife', 0)} %", "dataSectionId": "2bbd2ad2-3727-4a65-a646-3a8d565a9803", "dataFieldId": "9b3ccebf-8da6-40e6-9686-e83a6c44cb4e", "row": 0},
        {"value": f"{form_data.get('resistance_cell', 0):.0f} mΩ", "dataSectionId": "2bbd2ad2-3727-4a65-a646-3a8d565a9803", "dataFieldId": "52b13c9d-ac5c-4871-88b2-6fb10381f3fe", "row": 0},
        {"value": f"{form_data.get('resistance_pack', 0):.0f} mΩ", "dataSectionId": "2bbd2ad2-3727-4a65-a646-3a8d565a9803", "dataFieldId": "a6dad2ee-a3e7-4904-9584-0e9af35aa6f4", "row": 0},

        # Circularity
        {"value": f"{form_data.get('recycled_share_li', '-') }%", "dataSectionId": "a82c8ea5-7f2d-4f36-bcfd-8f1eb76740cf", "dataFieldId": "b2a62e2b-c378-4a51-9c37-75180e07f0ea", "row": 0},
        {"value": f"{form_data.get('recycled_share_ni', '-') }%", "dataSectionId": "a82c8ea5-7f2d-4f36-bcfd-8f1eb76740cf", "dataFieldId": "a292ecaa-339e-497d-a37e-3d67b72e6f17", "row": 0},
        {"value": f"{form_data.get('recycled_share_co', '-') }%", "dataSectionId": "a82c8ea5-7f2d-4f36-bcfd-8f1eb76740cf", "dataFieldId": "862a9d5f-60b4-4203-86b7-fd296f0568f3", "row": 0},
        {"value": f"{form_data.get('recycled_share_pb', '-') }%", "dataSectionId": "a82c8ea5-7f2d-4f36-bcfd-8f1eb76740cf", "dataFieldId": "22f48171-060c-46f4-a8e6-fa09379e39db", "row": 0},

        # Carbon Footprint
        {"value": f"{form_data.get('co2_per_functional_unit_pack', 0):.2f} kg CO₂ / kWh", "dataSectionId": "a4181719-e51d-45b7-b984-972df7edfb4f", "dataFieldId": "9373475c-43e8-4d7a-9365-8d7f79a26049", "row": 0},
        {"value": "A", "dataSectionId": "a4181719-e51d-45b7-b984-972df7edfb4f", "dataFieldId": "b1b59c4b-94b7-4893-9a38-265881a14639", "row": 0},
        {"value": f"{form_data.get('co2_percent_materials_pack', '-') } %", "dataSectionId": "a4181719-e51d-45b7-b984-972df7edfb4f", "dataFieldId": "d884cc77-7b9b-418e-a8c4-224a30186f85", "row": 0},
        {"value": f"{form_data.get('co2_percent_production_pack', '-') } %", "dataSectionId": "a4181719-e51d-45b7-b984-972df7edfb4f", "dataFieldId": "2f83d410-38d7-4273-be9b-d9227d1e53bc", "row": 0},
        {"value": f"{form_data.get('co2_percent_distribution_pack', '-') } %", "dataSectionId": "a4181719-e51d-45b7-b984-972df7edfb4f", "dataFieldId": "7b9781ce-4b8a-4166-9ac6-ebd8e0e442c4", "row": 0},
        {"value": f"{form_data.get('co2_percent_recycling_pack', '-') } %", "dataSectionId": "a4181719-e51d-45b7-b984-972df7edfb4f", "dataFieldId": "1046dfb4-2e39-4713-9409-0e49674b19fd", "row": 0},

    ]

