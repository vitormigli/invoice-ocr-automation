# 2. Disable oneDNN (`enable_mkldnn=False`) in PaddleOCR

## Status

Accepted — this is a workaround for a real bug, not a style preference.

## Context

On this project's CPU/Windows development environment, `PaddleOCR(...)` with
default settings (oneDNN/MKL-DNN enabled) raises at inference time:

```
NotImplementedError: (Unimplemented) ConvertPirAttribute2RuntimeAttribute not
support [pir::ArrayAttribute<pir::DoubleAttribute>]
```

This is a Paddle-internal incompatibility between the PIR (Paddle Intermediate
Representation) executor and the oneDNN backend for this model/op combination —
not a bug in this project's code.

## Decision

Always construct the OCR engine with `enable_mkldnn=False`
(`src/invoice_automation/ocr.py`). This is hardcoded, not a config flag, because
leaving it on breaks inference outright rather than just running slower.

## Consequences

- Slightly slower CPU inference than oneDNN would give, on platforms where oneDNN
  actually works — an acceptable trade for "the pipeline runs at all."
- If a deployment target reliably supports oneDNN with this PaddleOCR/PaddlePaddle
  version combination, that's worth re-testing before removing this flag —
  document the platform it was verified on if you do.
