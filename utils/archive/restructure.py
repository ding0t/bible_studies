#!/usr/bin/env python3
import shutil
import os
from pathlib import Path

docs = Path("docs")

moves = [
    # Prophecy studies
    ("studies/prophecy_events_times.md", "content/studies/prophecy/prophecy-events-times.md"),
    ("studies/day_is_near.md", "content/studies/prophecy/day-is-near.md"),
    ("studies/trumpet.md", "content/studies/prophecy/trumpet.md"),
    ("studies/rapture.md", "content/studies/prophecy/rapture.md"),
    ("studies/chart.md", "content/studies/prophecy/prophecy-chart.md"),
    
    # Theology studies
    ("studies/hebrew_roots.md", "content/studies/theology/hebrew-roots.md"),
    ("studies/numerology.md", "content/studies/theology/numerology.md"),
    
    # Spiritual disciplines
    ("studies/prayer.md", "content/studies/spiritual-disciplines/prayer.md"),
    ("studies/test_the_spirits.md", "content/studies/spiritual-disciplines/test-the-spirits.md"),
    ("studies/be_prepared.md", "content/studies/spiritual-disciplines/be-prepared.md"),
    
    # Sins
    ("studies/sin-idolatory.md", "content/studies/sins/idolatry.md"),
    ("studies/sin-sexual-immorality.md", "content/studies/sins/sexual-immorality.md"),
    ("studies/sin-sorcery.md", "content/studies/sins/sorcery.md"),
    
    # Teaching resources
    ("studies/on_teaching.md", "content/studies/teaching-resources/on-teaching.md"),
    ("sermons/sermon-howto.md", "content/studies/teaching-resources/sermon-howto.md"),
    
    # Hebrew
    ("learn-hebrew/hebrew-alphabet.md", "content/hebrew-studies/hebrew-alphabet.md"),
    ("learn-hebrew/resources.md", "content/hebrew-studies/resources.md"),
    
    # Sermons
    ("sermons/bible-prophecy-essentials.md", "content/sermons/bible-prophecy-essentials.md"),
    ("sermons/dispensational.md", "content/sermons/dispensational.md"),
    
    # Presentations (slides)
    ("slides/as-the-snake-was-lifted.md", "content/sermons/as-the-snake-was-lifted.md"),
    ("slides/hebrew-slides.md", "content/sermons/hebrew-slides.md"),
    ("slides/prophecy-essentials.md", "content/sermons/prophecy-essentials.md"),
    
    # Bible commentaries
    ("bible/by_book/01_genesis.md", "content/bible/commentaries/01-genesis.md"),
    ("bible/by_book/20_Proverbs.md", "content/bible/commentaries/20-proverbs.md"),
    ("bible/by_book/27_Daniel.md", "content/bible/commentaries/27-daniel.md"),
]

print("=" * 60)
print("RESTRUCTURING BIBLE STUDIES PROJECT")
print("=" * 60)

moved_count = 0
for src, dst in moves:
    src_path = docs / src
    dst_path = docs / dst
    
    if src_path.exists():
        # Create parent directory
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Move file
        shutil.move(str(src_path), str(dst_path))
        print(f"✓ {src} -> {dst}")
        moved_count += 1
    else:
        print(f"⚠ {src} (not found)")

# Move feasts directory
feasts_src = docs / "studies" / "feasts"
feasts_dst = docs / "content" / "studies" / "feasts"
if feasts_src.exists() and not feasts_dst.exists():
    shutil.move(str(feasts_src), str(feasts_dst))
    print(f"✓ Moved feasts/ directory")
    moved_count += 1

# Move dreams
dreams_src = docs / "dreams"
dreams_dst = docs / "content" / "dreams-visions"
if dreams_src.exists():
    if not dreams_dst.exists():
        dreams_dst.mkdir(parents=True, exist_ok=True)
    for item in dreams_src.glob("*.md"):
        shutil.move(str(item), str(dreams_dst / item.name))
        print(f"✓ {item.name} -> content/dreams-visions/")
        moved_count += 1

# Move investigation
investigation_src = docs / "investigation"
investigation_dst = docs / "content" / "studies" / "investigation" / "deliverance"
if investigation_src.exists():
    investigation_dst.mkdir(parents=True, exist_ok=True)
    for item in investigation_src.glob("*.md"):
        shutil.move(str(item), str(investigation_dst / item.name))
        print(f"✓ {item.name} -> content/studies/investigation/deliverance/")
        moved_count += 1

print(f"\n✓ Total files/dirs moved: {moved_count}")
print("\n" + "=" * 60)
print("CONSOLIDATING IMAGES")
print("=" * 60)

# Consolidate images
img_src = docs / "img"
img_dst = docs / "assets" / "img"
if img_src.exists():
    for item in img_src.rglob("*"):
        rel_path = item.relative_to(img_src)
        dst_item = img_dst / rel_path
        if item.is_dir():
            dst_item.mkdir(parents=True, exist_ok=True)
        else:
            dst_item.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(item), str(dst_item))
    print("✓ Copied all images to assets/img/")

print("\n" + "=" * 60)
print("CLEANUP")
print("=" * 60)

# Remove empty directories
empty_dirs = [
    "learn-hebrew", "sermons", "slides", "dreams", 
    "investigation", "img", "studies", "prophecy_and_events"
]

for dirname in empty_dirs:
    dirpath = docs / dirname
    if dirpath.exists():
        try:
            # Check if directory is empty
            if not list(dirpath.glob("*")):
                dirpath.rmdir()
                print(f"✓ Removed empty directory: {dirname}/")
        except OSError:
            pass  # Directory not empty or other error

print("\n" + "=" * 60)
print("RESTRUCTURING COMPLETE!")
print("=" * 60)
