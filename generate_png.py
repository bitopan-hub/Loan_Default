import base64
import urllib.request
import sys
import os

# Diagram 1: Overall Project Flow
project_graph = """
flowchart TD
    subgraph Frontend [React Frontend - Port 3000]
        UI[User Interface / Pages]
        AuthC[Auth Context & Protected Routes]
        Charts[Chart.js Visualizations]
        API_Client[Axios HTTP Client]
        
        UI -->|Interacts| AuthC
        UI -->|Renders| Charts
        UI -->|Triggers Requests| API_Client
    end

    subgraph Backend [Flask Backend - Port 5000]
        API_Routes[Flask API Endpoints]
        Auth_Middleware[JWT Token Decorator]
        
        subgraph ML_Pipeline [Machine Learning & XAI]
            Preprocess[preprocessing.py / Pandas]
            Model[(loan_model_bundle.pkl)]
            SHAP[xai.py / SHAP Explainer]
        end
        
        DB_Driver[MySQL Connector]
    end

    subgraph Database [MySQL Database]
        Users_Table[(Users Table)]
        Customers_Table[(Customers Table)]
    end

    API_Client -- HTTP Requests --> API_Routes
    API_Routes --> Auth_Middleware
    
    Auth_Middleware -- Validate Token --> API_Routes
    API_Routes -- Login/Register/Reset --> DB_Driver
    DB_Driver <--> Users_Table

    API_Routes -- GET/POST/PUT/DELETE --> DB_Driver
    API_Routes -- Analytics Queries --> DB_Driver
    DB_Driver <--> Customers_Table
    
    API_Routes -- /predict --> Preprocess
    Preprocess -- Format Data --> Model
    Model -- Prediction & Probabilities --> SHAP
    SHAP -- Feature Explanations --> API_Routes
    API_Routes -- JSON Response --> API_Client
"""

# Diagram 2: Backend Only Flow
backend_graph = """
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

def save_diagram(graph_text, filename):
    try:
        graph_bytes = graph_text.encode('utf-8')
        base64_bytes = base64.b64encode(graph_bytes)
        base64_string = base64_bytes.decode('utf-8')
        url = f'https://mermaid.ink/img/{base64_string}?scale=3'
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with open(filename, 'wb') as out_file:
                out_file.write(response.read())
        print(f'SUCCESS: Saved {filename}')
    except Exception as e:
        print(f'ERROR saving {filename}: {e}')

if __name__ == "__main__":
    base_path = "C:\\Users\\bitop\\Loan_Default\\"
    save_diagram(project_graph, os.path.join(base_path, "Project_Flow_Diagram.png"))
    save_diagram(backend_graph, os.path.join(base_path, "Backend_Flow_Diagram.png"))
