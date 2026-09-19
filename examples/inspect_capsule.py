from iap.resources import teacher_capsule

if __name__ == "__main__":
    capsule = teacher_capsule("transformer")
    print({"policy_bytes": len(capsule.policy.raw), "atlas_bytes": len(capsule.atlas),
           "payload_bytes": capsule.payload_bytes, "wire_bytes": len(capsule.to_envelope()),
           "sha256": capsule.sha256})
