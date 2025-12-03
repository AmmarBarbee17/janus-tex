from __future__ import annotations

import os
import sys

try:
	import google.generativeai as genai
except ImportError:
	print("Install google-generativeai to list Gemini models.", file=sys.stderr)
	raise SystemExit(1)


def main() -> int:
	api_key = os.environ.get("GOOGLE_API_KEY")
	if not api_key:
		print("Set the GOOGLE_API_KEY environment variable before running this script.", file=sys.stderr)
		return 1

	genai.configure(api_key=api_key)
	try:
		models = list(genai.list_models())
	except Exception as exc:  # pragma: no cover - network/runtime issues
		print(f"Failed to query models: {exc}", file=sys.stderr)
		return 1

	for model in models:
		methods = getattr(model, "supported_generation_methods", []) or ["-"]
		methods_str = ", ".join(methods)
		print(f"{model.name} -> {methods_str}")

	return 0


if __name__ == "__main__":
	raise SystemExit(main())