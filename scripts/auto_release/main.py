import os
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
_LOG = logging.getLogger(__name__)

class AzureSdkAutomation:
    def __init__(self):
        # --- CONFIGURAÇÕES - PREENCHA AQUI ---
        self.issue_link = "LINK_DA_ISSUE_QUE_VOCE_CRIOU"  # Ex: https://github.com/Azure/sdk-release-request/issues/123
        self.bot_token = os.getenv("BOT_TOKEN") 
        self.spec_readme = "URL_DO_README_SWAGGER" # O link do readme.md no repo azure-rest-api-specs
        # -------------------------------------

        self.whole_package_name = ""
        self.new_branch = ""
        self.temp_folder = "./temp_codegen"

    def run_command(self, cmd, critical=True):
        _LOG.info(f"Executando: {cmd}")
        result = subprocess.run(cmd, shell=True, check=critical)
        return result

    def generate_code(self):
        """Gera o código usando o sdk_generator."""
        input_data = {
            "headSha": "main", # Ou o commit específico da spec
            "repoHttpsUrl": "https://github.com/Azure/azure-rest-api-specs",
            "specFolder": "azure-rest-api-specs",
            "relatedReadmeMdFiles": [self.spec_readme.split("specification")[-1]],
            "runMode": "auto-release",
        }
        
        Path(self.temp_folder).mkdir(parents=True, exist_ok=True)
        res_path = Path(self.temp_folder) / "temp.json"
        
        with open(res_path, "w") as f:
            json.dump(input_data, f)
        
        # Executa o gerador
        self.run_command(f"sdk_generator {res_path} {res_path}")
        
        # Carrega o nome do pacote descoberto
        with open(res_path, "r") as f:
            res = json.load(f)
            self.whole_package_name = res["packages"][0]["packageName"]

    def prepare_git_branch(self):
        """Cria uma nova branch para não sujar a main."""
        # Garante que estamos na main limpa antes de começar
        self.run_command("git checkout main")
        self.run_command("git pull origin main")
        
        # Cria branch única: codegen-dns-20260222
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.new_branch = f"codegen-{self.whole_package_name}-{timestamp}"
        
        _LOG.info(f"Criando nova branch: {self.new_branch}")
        self.run_command(f"git checkout -b {self.new_branch}")

    def commit_and_push(self):
        """Faz o commit e sobe para o seu fork."""
        self.run_command("git add sdk/")
        
        # Mensagem de commit dinâmica
        commit_msg = f"Codegen and tests for {self.whole_package_name}"
        self.run_command(f'git commit -m "{commit_msg}"')
        
        _LOG.info(f"Enviando branch {self.new_branch} para o GitHub...")
        self.run_command(f"git push origin {self.new_branch}")

    def print_pr_instructions(self):
        """Exibe o que você deve colar na Web."""
        print("\n" + "="*50)
        print("CÓDIGO ENVIADO COM SUCESSO!")
        print("="*50)
        print(f"1. Vá ao GitHub e selecione a branch: {self.new_branch}")
        print(f"2. Título do PR: [AutoRelease] {self.whole_package_name} release")
        print(f"3. Descrição do PR:\n")
        print(f"This PR is generated for the release issue: {self.issue_link}")
        print(f"\nBuildTargetingString\n  {self.whole_package_name}")
        print("Skip.CreateApiReview")
        print("="*50)

    def start(self):
        self.generate_code()
        self.prepare_git_branch()
        self.commit_and_push()
        self.print_pr_instructions()

if __name__ == "__main__":
    automation = AzureSdkAutomation()
    automation.start()
