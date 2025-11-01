import sys
from collections import defaultdict


def parse_and_summarize(symbol_file: str):
    """Quickly parse and display summary"""
    symbols = []

    print(f"\n📊 Analyzing {symbol_file}...\n")

    with open(symbol_file, 'r') as f:
        lines = f.readlines()

    # Mega Drive memory map
    ROM_START = 0x000000
    ROM_END = 0x400000  # 4MB max
    RAM_START = 0xE00000  # RAM starts here

    prev_address = 0
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        if len(parts) < 3:
            continue

        try:
            address = int(parts[0], 16)
            symbol_type = parts[1]
            symbol_name = parts[2]

            # Ignore symbols in RAM (they don't go to ROM)
            if address >= RAM_START or address >= ROM_END:
                continue

            size = 0
            if i < len(lines) - 1:
                # Find the next valid symbol in ROM
                for j in range(i + 1, len(lines)):
                    next_line = lines[j].strip()
                    if next_line:
                        next_parts = next_line.split()
                        if len(next_parts) >= 1:
                            try:
                                next_address = int(next_parts[0], 16)
                                if next_address >= RAM_START:
                                    break
                                if next_address > address:
                                    size = next_address - address
                                    break
                            except:
                                pass

            if symbol_name.endswith('_size'):
                try:
                    size = address
                except:
                    pass

            # Ignore very large symbols (there may still be issues)
            if size > 0 and size < 10 * 1024 * 1024:
                symbols.append({
                    'address': address,
                    'size': size,
                    'type': symbol_type,
                    'name': symbol_name
                })

        except ValueError:
            continue

    # Categorize
    categories = defaultdict(list)

    total_size = 0

    symbols = list(filter(lambda s: not s['name'].endswith('_size') and s['size'] > 16, symbols))

    for symbol in symbols:
        name = symbol['name'].lower()
        total_size += symbol['size']
        if 'sprite' in name:
            categories['Sprites'].append(symbol)
            symbol['category'] = 'Sprite'
        elif 'tileset' in name:
            categories['Tilesets'].append(symbol)
            symbol['category'] = 'Tileset'
        elif 'image' in name:
            categories['Images'].append(symbol)
            symbol['category'] = 'Image'
        elif 'map' in name in name:
            categories['Maps'].append(symbol)
            symbol['category'] = 'Map'
        elif 'palette' in name or '_pal' in name:
            categories['Palettes'].append(symbol)
            symbol['category'] = 'Palette'
        elif 'xgm' in name or 'music' in name or 'sound' in name or 'audio' in name or 'sfx' in name:
            categories['Audio'].append(symbol)
            symbol['category'] = 'Audio'
        elif 'tilemap' in name:
            categories['Tilemaps'].append(symbol)
            symbol['category'] = 'Tilemap'
        elif 'font' in name:
            categories['Fonts/Text'].append(symbol)
            symbol['category'] = 'Font/Text'
        elif name.startswith('_') or symbol['type'] in ['T', 't']:
            categories['Code'].append(symbol)
            symbol['category'] = 'Code'
        else:
            categories['Other'].append(symbol)
            symbol['category'] = 'Other'

    # Calculate totals
    category_sizes = {cat: sum(s['size'] for s in syms)
                      for cat, syms in categories.items()}

    # Display summary
    print("=" * 100)
    print("📈 MEMORY USAGE SUMMARY")
    print("=" * 100)
    print(f"\n✅ Total symbols: {len(symbols):,}")
    print(f"💾 Total memory: {total_size:,} bytes ({total_size / 1024:.2f} KB)")
    print()

    # Top categories
    print("-" * 100)
    print("🏆 USAGE BY CATEGORY")
    print("-" * 100)
    print()

    sorted_categories = sorted(category_sizes.items(), key=lambda x: x[1], reverse=True)

    for category, size in sorted_categories:
        if size > 0:
            percentage = (size / total_size * 100) if total_size > 0 else 0
            symbol_count = len(categories[category])
            bar_length = int(percentage / 2)  # Scale to max 50 characters
            bar = '█' * bar_length

            print(f"{category:20s} {bar:30s} {size / 1024:7.2f} KB ({percentage:5.2f}%) - {symbol_count:4d} symbols")

    # Top 10 symbols
    print()
    print("-" * 100)
    print("🔝 TOP MEMORY-CONSUMING SYMBOLS")
    print("-" * 100)
    print()

    top_symbols = sorted(symbols, key=lambda x: x['size'], reverse=True)
    for i, symbol in enumerate(top_symbols, 1):
        print(f"{i:2d}. {symbol['name']:65s} {symbol['category']:10s}{symbol['size'] / 1024:8.2f} KB")

if __name__ == '__main__':
    symbol_file = 'symbol.txt'
    if len(sys.argv) > 1:
        symbol_file = sys.argv[1]

    try:
        parse_and_summarize(symbol_file)
    except FileNotFoundError:
        print(f"\n❌ Error: File '{symbol_file}' not found!")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)
