import argparse
import json
import shutil
import subprocess
from pathlib import Path


def compile_cpp(cpp_path: Path, binary_path: Path) -> None:
    compiler = shutil.which("g++")
    if compiler is None:
        raise RuntimeError("g++ not found. Install a C++ compiler first.")

    cmd = [compiler, str(cpp_path), "-O2", "-std=c++17", "-o", str(binary_path)]
    subprocess.run(cmd, check=True)


def run_profile(binary_path: Path, input_csv: Path) -> dict:
    proc = subprocess.run([str(binary_path), str(input_csv)], check=True, capture_output=True, text=True)
    return json.loads(proc.stdout)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile and run C++ risk profiler")
    parser.add_argument("--cpp", default="extensions/cpp/risk_profile.cpp")
    parser.add_argument("--csv", default="data/raw/risk_factors_cervical_cancer.csv")
    parser.add_argument("--bin", default="outputs/risk_profile")
    parser.add_argument("--out", default="outputs/tables/cpp_risk_profile.json")
    args = parser.parse_args()

    cpp_path = Path(args.cpp)
    input_csv = Path(args.csv)
    binary_path = Path(args.bin)
    out_path = Path(args.out)

    binary_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    compile_cpp(cpp_path, binary_path)
    result = run_profile(binary_path, input_csv)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
