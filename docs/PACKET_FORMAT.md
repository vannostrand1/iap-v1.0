# Byte-level formats

## Historical policy: IAPCV2 (97 bytes)

All tensor storage is row-major; all scales are little-endian IEEE float32.

| Offset | Bytes | Content |
|---:|---:|---|
| 0 | 7 | ASCII `IAPCV2` followed by NUL |
| 7 | 16 | Four positive finite scales: w1, b1, w2, b2 |
| 23 | 48 | int8 first-layer matrix, shape (8, 6) |
| 71 | 8 | int8 first-layer bias |
| 79 | 16 | int8 output matrix, shape (2, 8) |
| 95 | 2 | int8 output bias |

Dequantize each tensor by multiplying by its own scale.
`q(x) = tanh(x @ w1.T + b1) @ w2.T + b2`.
Raw files have no checksum. Their headers/scales/lengths are validated, but
undetected value changes remain possible without an external hash/envelope.

## Historical relational capsule (241 bytes)

The first 97 bytes are a policy. The next 144 bytes are 24 × 6 signed int8 source
observations, ordered as eight contiguous three-state chains. This order is
structural side information. The atlas is a complete support table, not a
recipient map. The legacy format carries no explicit topology generalization:
the eight/three/six dimensions are part of its schema.

## v1 envelope

`IAPENV1\0` (8 bytes), followed by a little-endian uint32 JSON-header length,
UTF-8 JSON metadata, and the raw 97- or 241-byte payload. Required metadata:
`schema_version=1`, `policy_format=IAPCV2`, atlas format or null,
`payload_bytes`, and `payload_sha256`.

The parser bounds total size to 16,384 bytes and JSON metadata to 8,192 bytes,
rejects unsupported formats, and checks the raw payload hash. It does not
execute code, accept pickle, infer a model class, or follow links.

The envelope is deliberately larger than the legacy payload. Reports distinguish
policy bytes, atlas bytes, total payload bytes and framed wire bytes. Framing,
shared interpreter/schema, calibration labels and recipient observations are
not included in historical claims of a 97- or 241-byte cultural payload.

These byte counts do not prove compression optimality. Given an agreed ordering,
the 24 binary source decisions could themselves be bit-packed into three bytes.
A truth-table transport baseline is therefore an important publication control;
it is not claimed to have been measured by this release.
