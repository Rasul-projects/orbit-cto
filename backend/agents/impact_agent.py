import os
import json
import subprocess
from google import genai
from google.genai import types

client = genai.Client()

def get_orbit_graph_context(target_component: str) -> str:
    try:
        result = subprocess.run(
            ["glab", "orbit", "query", f"--component={target_component}"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except Exception:
        pass
    
    mock_orbit_graph = {
        "component": target_component,
        "type": "microservice",
        "connections": [
            {"target": "checkout-api", "relation": "depends_on", "risk": "High"},
            {"target": "billing-dashboard", "relation": "downstream_event_listener", "risk": "Medium"},
            {"target": "refund-system", "relation": "direct_import", "risk": "High"},
            {"target": "analytics-pipeline", "relation": "data_producer", "risk": "Low"}
        ],
        "active_pipelines": ["pipeline_#88421_failed", "pipeline_#88410_passed"],
        "recent_mrs": [{"id": 402, "title": "Refactor payment mutations", "author": "John"}]
    }
    return json.dumps(mock_orbit_graph, indent=2)

def analyze_impact(component_name: str) -> str:
    orbit_data = get_orbit_graph_context(component_name)
    
    prompt = f"""
    You are Orbit CTO, an AI Executive Engineer. Analyze the following GitLab Orbit Knowledge Graph data for the component '{component_name}'.
    
    Provide a strategic impact evaluation matching this exact executive format:
    
    ### 💥 Impact Analysis: {component_name}
    **Estimated Blast Radius:** [High/Medium/Low]
    
    #### Affected Downstream Systems:
    - [System Name] ([Relation Type]) -> Risk Level
    
    #### Executive Summary & Recommendation:
    [2 sentence blunt risk assessment based on pipeline state and code coupling]
    
    Raw Orbit Graph Context:
    {orbit_data}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "payment-service"
    print(analyze_impact(target))
