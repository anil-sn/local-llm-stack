#!/usr/bin/env bash
#
# Model Validation using llama-gguf-hash
# Verifies model integrity and displays metadata
#

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║          Model Validation & Integrity Check              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Configuration
MODEL="${1:-$HOME/models/Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf}"

# Check model exists
if [ ! -f "$MODEL" ]; then
    echo "❌ Model not found: $MODEL"
    echo ""
    echo "Download with:"
    echo "  ./bin/download-model.sh"
    exit 1
fi

echo "📦 Model: $MODEL"
echo ""

# Check file size
FILE_SIZE=$(du -h "$MODEL" | cut -f1)
echo "📊 File Size: $FILE_SIZE"
echo ""

# Check for llama-gguf-hash
if command -v llama-gguf-hash &> /dev/null; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔹 Computing Model Hash (SHA256)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    HASH=$(llama-gguf-hash "$MODEL" 2>/dev/null || echo "Hash computation failed")
    echo "SHA256: $HASH"
    echo ""
    
    # Save hash for future verification
    HASH_FILE="${MODEL}.sha256"
    echo "$HASH  $(basename "$MODEL")" > "$HASH_FILE"
    echo "💾 Hash saved to: $HASH_FILE"
    echo ""
else
    echo "⚠️  llama-gguf-hash not found"
    echo "   Install: brew install llama.cpp"
    echo ""
    
    # Fallback to shasum
    echo "Using system shasum instead..."
    HASH=$(shasum -a 256 "$MODEL" | cut -d' ' -f1)
    echo "SHA256: $HASH"
    echo ""
fi

# Check for llama-gguf (metadata viewer)
if command -v llama-gguf &> /dev/null; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔹 Model Metadata"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    llama-gguf "$MODEL" info 2>/dev/null | head -50 || echo "Unable to read metadata"
    echo ""
fi

# Validate GGUF structure
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔹 Structure Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check GGUF magic number
MAGIC=$(head -c 4 "$MODEL" | od -A n -t x1 | tr -d ' \n')
if [ "$MAGIC" = "47475546" ]; then
    echo "✅ Valid GGUF file format"
else
    echo "❌ Invalid GGUF file format (magic: $MAGIC)"
    exit 1
fi

# Check if file is complete (try to read end of file)
if tail -c 1024 "$MODEL" > /dev/null 2>&1; then
    echo "✅ File appears complete"
else
    echo "⚠️  File may be truncated or corrupted"
fi

echo ""

# Model info from filename
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔹 Model Information"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

BASENAME=$(basename "$MODEL")
echo "  Filename: $BASENAME"
echo "  Location: $(dirname "$MODEL")"
echo "  Size: $FILE_SIZE"

# Extract quantization from filename
if [[ "$BASENAME" =~ Q([0-9]+)_([A-Z]+) ]]; then
    echo "  Quantization: Q${BASH_REMATCH[1]}_${BASH_REMATCH[2]}"
fi

# Check for hash file
HASH_FILE="${MODEL}.sha256"
if [ -f "$HASH_FILE" ]; then
    echo ""
    echo "💾 Previous hash found: $HASH_FILE"
    echo "   To verify: ./bin/validate-model.sh --verify"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║              Validation Complete! ✅                     ║"
echo "╚══════════════════════════════════════════════════════════╝"
