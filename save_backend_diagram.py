import base64
import urllib.request
import os

graph = """
flowchart TD
    subgraph API_Entry [API Request Entry]
        Req[Incoming HTTP Request] --> Auth{JWT Check}
    end

    subgraph Security_Layer [Security & Middleware]
        Auth -- Invalid --> Err401[401 Unauthorized]
        Auth -- Valid --> Route{Route Handler}
    end

    subgraph Data_Ops [Database Operations]
        Route -- CRUD / Analytics --> DB_Conn[MySQL Connection]
        DB_Conn --> SQL[Parameterized Query]
        SQL --> DB[(MySQL DB)]
        DB --> DB_Res[Data Result]
    end

    subgraph ML_Engine [Predictive Engine]
        Route -- /predict --> Pre[preprocessing.py]
        Pre -- Feature Scaling --> Model[loan_model_bundle.pkl]
        Model -- Probabilities --> Decision[Decision Logic]
        
        subgraph XAI_Module [Explainable AI]
            Model --> SHAP[xai.py / SHAP]
            SHAP --> Expl[Feature Contributions]
        end
    end

    subgraph Response_Gen [Response Assembly]
        DB_Res --> JSON[JSON Formatter]
        Decision --> JSON
        Expl --> JSON
        JSON --> Res[HTTP Response]
    end

    style API_Entry fill:#f9f,stroke:#333,stroke-width:2px
    style ML_Engine fill:#bbf,stroke:#333,stroke-width:2px
    style Data_Ops fill:#bfb,stroke:#333,stroke-width:2px
    style Security_Layer fill:#fbb,stroke:#333,stroke-width:2px
"""

def save_diagram():
    try:
        graph_bytes = graph.encode('utf-8')
        base64_bytes = base64.b64encode(graph_bytes)
        base64_string = base64_bytes.decode('utf-8')
        url = f'https://mermaid.ink/img/{base64_string}?scale=3'
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with open("C:/Users/bitop/Loan_Default/Backend_Flow_Diagram.png", 'wb') as out_file:
                out_file.write(response.read())
        print("SUCCESS")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    save_diagram()
