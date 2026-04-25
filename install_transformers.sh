#!/bin/bash
echo "🚀 Starting Transformer Installation..."
echo "This will take time. Don't interrupt!"

# Activate venv
source venv/bin/activate

# Upgrade pip first (with resume)
pip install --upgrade pip

# Install PyTorch CPU-only (much smaller than full PyTorch)
echo "📦 Installing PyTorch CPU (1.2GB)..."
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install transformers
echo "🤖 Installing Transformers (300MB)..."
pip install transformers

# Install additional dependencies
echo "📚 Installing Accelerate and others..."
pip install accelerate sentencepiece scikit-learn

# Test installation
echo "✅ Testing installation..."
python -c "from transformers import pipeline; print('✓ Transformers imported successfully')"

echo "✅ Installation Complete!"
