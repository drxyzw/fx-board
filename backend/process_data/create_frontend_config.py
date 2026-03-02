from dotenv import load_dotenv
import os

load_dotenv()
frontend_dir = os.getenv("FRONTEND_CONFIG_DIR")
neer_base_year = os.getenv("NEER_BASE_YEAR")

with open(frontend_dir + "/configByBackend.js", "w") as f:
    # f.write("export const CONFIG_BACKEND = {\n")
    # f.write("\tNEER_BASE_YEAR: " + neer_base_year + ",\n")
    # f.write("}\n")
    f.write("const NEER_BASE_YEAR = \"" + neer_base_year + "\";\n")
