import os
import glob
from datetime import datetime

def analyze_logs():
    # Encontrar o arquivo de log mais recente
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        print(f"Diretório de logs não encontrado: {log_dir}")
        return

    log_files = glob.glob(os.path.join(log_dir, 'app_debug_*.log'))
    if not log_files:
        print("Nenhum arquivo de log encontrado")
        return

    latest_log = max(log_files, key=os.path.getctime)
    print(f"\nAnalisando arquivo: {latest_log}")
    print(f"Última modificação: {datetime.fromtimestamp(os.path.getmtime(latest_log))}\n")

    try:
        # Tentar diferentes codificações
        encodings = ['utf-8', 'latin1', 'cp1252']
        log_content = None
        
        for encoding in encodings:
            try:
                with open(latest_log, 'r', encoding=encoding) as f:
                    log_content = f.read()
                break
            except UnicodeDecodeError:
                continue

        if log_content is None:
            print("Não foi possível ler o arquivo de log com nenhuma codificação suportada")
            return

        # Contadores de erros
        error_count = 0
        warning_count = 0
        critical_count = 0

        print("=== Análise de Logs do Data Manager Pro ===\n")

        print("Erros Críticos encontrados:")
        for line in log_content.split('\n'):
            if 'CRITICAL' in line:
                print(f"- {line.strip()}")
                critical_count += 1
        print(f"Total de erros críticos: {critical_count}\n")

        print("Erros encontrados:")
        for line in log_content.split('\n'):
            if 'ERROR' in line:
                print(f"- {line.strip()}")
                error_count += 1
        print(f"Total de erros: {error_count}\n")

        print("Avisos encontrados:")
        for line in log_content.split('\n'):
            if 'WARNING' in line:
                print(f"- {line.strip()}")
                warning_count += 1
        print(f"Total de avisos: {warning_count}\n")

        print("Métricas de Performance:")
        for line in log_content.split('\n'):
            if any(metric in line for metric in ['Memory Usage:', 'CPU Usage:', 'Uptime:']):
                print(f"- {line.strip()}")

        print("\nResumo:")
        print(f"- Erros Críticos: {critical_count}")
        print(f"- Erros: {error_count}")
        print(f"- Avisos: {warning_count}")

    except Exception as e:
        print(f"Erro ao analisar logs: {str(e)}")

if __name__ == "__main__":
    analyze_logs()
