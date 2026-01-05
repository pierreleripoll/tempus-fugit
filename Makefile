.PHONY: help install main weird festival all clean

# Default target
help:
	@echo "Tempus Fugit - Timer Video Generator"
	@echo ""
	@echo "Available commands:"
	@echo "  make install   - Install dependencies using uv"
	@echo "  make main      - Generate clean countdown timer (2:30)"
	@echo "  make weird     - Generate glitchy timer with effects (1:00)"
	@echo "  make festival  - Generate festival timer with chaos (2:00)"
	@echo "  make all       - Generate all three timers"
	@echo "  make clean     - Remove generated videos from output/"
	@echo "  make help      - Show this help message"

# Install dependencies with uv
install:
	@echo "Installing dependencies with uv..."
	uv pip install -r requirements.txt
	@echo "✓ Dependencies installed"

# Generate clean timer
main:
	@echo "Generating clean countdown timer..."
	python main.py

# Generate weird glitchy timer
weird:
	@echo "Generating weird glitchy timer..."
	python weird.py

# Generate festival chaos timer
festival:
	@echo "Generating festival timer with animations..."
	python festival.py

# Generate all timers
all: main weird festival
	@echo "✓ All timers generated"

# Clean output directory
clean:
	@echo "Cleaning output directory..."
	rm -f output/*.mp4
	@echo "✓ Output directory cleaned"
