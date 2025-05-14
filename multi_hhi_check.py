import argparse
import subprocess
import os
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def get_status_color(code):
    try:
        code = int(code)
        if 200 <= code < 300:
            return Fore.GREEN + str(code) + Style.RESET_ALL
        elif 300 <= code < 400:
            return Fore.RED + str(code) + Style.RESET_ALL
        elif 400 <= code < 500:
            return Fore.YELLOW + str(code) + Style.RESET_ALL
        elif 500 <= code < 600:
            return Fore.RED + str(code) + Style.RESET_ALL
    except:
        return Fore.WHITE + "N/A" + Style.RESET_ALL
    return str(code)

def extract_status_line(output):
    for line in output.splitlines():
        if line.startswith("HTTP/"):
            return line
    return "No HTTP response found"

def run_curl(domain, injected_host):
    results = ""

    urls = [
        ("https://" + domain.lstrip("http://").lstrip("https://"), "HTTPS"),
        ("http://" + domain.lstrip("http://").lstrip("https://"), "HTTP")
    ]

    for url, scheme in urls:
        try:
            cmd = [
                "curl", "-i", "-k", url,
                "-H", f"Host: {injected_host}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            header = f"\n{Fore.CYAN}{'='*10} {scheme} REQUEST TO {url} {'='*10}{Style.RESET_ALL}"
            status_line = extract_status_line(result.stdout)
            status_code = status_line.split()[1] if len(status_line.split()) > 1 else "N/A"
            colored_status = get_status_color(status_code)

            summary = f"{Fore.MAGENTA}[i] Status: {colored_status} | Host: {injected_host}{Style.RESET_ALL}\n"
            results += header + "\n" + summary + result.stdout + "\n"
        except subprocess.TimeoutExpired:
            results += f"\n{Fore.LIGHTBLACK_EX}[!] Timeout expired for {url}{Style.RESET_ALL}\n"
        except Exception as e:
            results += f"\n{Fore.LIGHTBLACK_EX}[!] Error for {url}: {e}{Style.RESET_ALL}\n"

    return results

def main():
    parser = argparse.ArgumentParser(description="🌐 Host Header Injection Tester with Sexy Output")
    parser.add_argument("file", help="Path to file with list of domains")
    parser.add_argument("--host", default="evil.com", help="Injected Host header (default: evil.com)")
    parser.add_argument("--output", help="Optional output file to save results")

    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"{Fore.RED}[!] File not found: {args.file}{Style.RESET_ALL}")
        return

    with open(args.file, "r") as f:
        domains = [line.strip() for line in f if line.strip()]

    all_results = ""

    for domain in domains:
        print(f"{Fore.BLUE}[+] Testing domain: {domain}{Style.RESET_ALL}")
        results = run_curl(domain, args.host)
        all_results += results
        print(results)

    if args.output:
        with open(args.output, "w") as out:
            out.write(all_results)
        print(f"\n{Fore.GREEN}[✓] Results saved to {args.output}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
