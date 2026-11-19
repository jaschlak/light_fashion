# V1 travel parts and packing checklist

This list is organized for working away from home. The **minimum kit** is enough
to make the 30 cm strip illuminate over USB. The expanded kit adds diffuser and
shirt-construction experiments.

## Minimum kit: do not leave without these

### Known hardware

- [ ] Adafruit HUZZAH32 ESP32 Feather, product 3591
- [ ] WS2812 5 V, 60 LED/m strip reel
- [ ] External antenna only if choosing a Lonely Binary board instead of the
      HUZZAH32; it is not needed for the HUZZAH32
- [ ] Existing black shirt

### Power and programming

- [ ] 5 V USB wall adapter rated at least 1 A; 2 A is preferable
- [ ] If using a wall adapter with exposed leads: photograph its label and
      bring it only if it is marked regulated 5 V DC
- [ ] Two-position terminal block, WAGO-style lever connectors, or another
      insulated way to join and split the bare power leads
- [ ] Micro-USB **data** cable for the HUZZAH32
- [ ] Laptop
- [ ] Laptop charger
- [ ] Arduino IDE and ESP32 board support already installed, or internet access
      for setup

### Small electrical parts

- [ ] One 330–470 ohm resistor for the NeoPixel data line
- [ ] One 500–1000 microfarad electrolytic capacitor rated 6.3 V or higher
- [ ] 22–26 AWG stranded hookup wire; ideally red, black/white, and green
- [ ] Breadboard and male/female jumper wires, if available
- [ ] Three-pin removable connector, if available
- [ ] Heat-shrink tubing in small sizes
- [ ] Electrical tape or other nonconductive tape

### Electronics tools

- [ ] Temperature-controlled soldering iron
- [ ] Iron stand and damp sponge or brass tip cleaner
- [ ] Electronics solder
- [ ] Flux pen or paste
- [ ] Wire cutters
- [ ] Wire strippers
- [ ] Needle-nose pliers
- [ ] Multimeter with probes
- [ ] Helping hands, PCB vise, or small clamps
- [ ] Heat gun for heat-shrink, if available
- [ ] Desoldering braid or pump for mistakes
- [ ] Nonflammable or heat-resistant bench surface

## Diffuser experiment kit

Bring several scraps rather than committing to one material before testing.

- [ ] White translucent polyester, organza, ripstop, or similar fabric
- [ ] Optional black sheer mesh to hide the white diffuser while unlit
- [ ] Non-stretch woven fabric or 20–25 mm grosgrain ribbon, at least 40 cm long
- [ ] Two narrow spacer strips, piping cord, foam, or spacer mesh for a 5–10 mm
      air gap
- [ ] Extra spacer material for testing 15 mm separation
- [ ] Painter's tape or removable double-sided tape for bench mockups only
- [ ] Ruler or measuring tape
- [ ] Camera/phone for comparison photographs at the same exposure and distance

Do not use paper as the final wearable diffuser. Paper may be useful for a
brief optical comparison on the unpowered or low-power bench setup, but it is
not a durable garment material.

## Sewing and garment kit

- [ ] Sewing machine and power cord, unless one is already at the destination
- [ ] Black polyester thread
- [ ] Hand-sewing needles
- [ ] Fabric scissors
- [ ] Small utility scissors or thread snips
- [ ] Seam ripper
- [ ] Fabric clips or pins
- [ ] Tailor's chalk or washable fabric marker
- [ ] Flexible measuring tape
- [ ] Black woven or knit fabric scraps for retaining loops and eventual pockets
- [ ] Hook-and-loop tape, snaps, or small buttons for removable closures
- [ ] Safety pins for the unpowered placement test

## Optional but useful

- [ ] USB power meter for measuring total current
- [ ] Infrared thermometer or contact temperature probe
- [ ] Spare HUZZAH32 or one Lonely Binary ESP32 board
- [ ] Spare resistor and capacitor
- [ ] Spare three-wire connector
- [ ] Small labeled bags or parts organizer
- [ ] Notebook and pen
- [ ] Calipers

## Do not pack or use

- [ ] **Do not bring the old swollen PKCELL LP803860 battery as a power source.**
      Keep it isolated for damaged-battery disposal.
- [ ] Do not plan to power the complete five-meter reel through the Feather.
- [ ] Do not use loose, unlabeled, damaged, or reverse-polarity batteries.
- [ ] Do not wear the loose bench wiring.

## Before leaving home

1. Put the resistor and capacitor in a labeled bag; they are the easiest items
   to forget.
2. Confirm the Micro-USB cable transfers data, not only power.
3. Confirm the wall adapter is marked 5 V and at least 1 A.
4. Pack the multimeter; exposed-lead polarity must be measured rather than
   guessed from insulation color.
5. Open the [bare-lead wiring diagram](../../diagrams/huzzah32-wall-wart-wiring.svg)
   on the laptop or save it for offline access.
6. Confirm the soldering iron, laptop, and sewing machine power cords are packed.
7. Keep the LED reel protected from tight bends and crushing during transport.

## Before applying power

Use only a 30 cm, 18-pixel segment. Verify `VCC`, `GND`, and `DIN`, capacitor
polarity, and common ground with power disconnected. Start at 10% brightness
and stop for heat, odor, flicker, resets, or unstable connections.

