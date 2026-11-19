# HUZZAH32 and WS2812 bench test

This procedure is for the current 5 V bench test. It is not the final
battery-powered garment circuit. Two safe power approaches are documented:
Micro-USB power, or a verified regulated 5 V DC wall adapter with bare leads.

Open the [illustrated wiring diagram](../diagrams/huzzah32-neopixel-usb-wiring.html)
in a browser while wiring.

For a wall adapter with bare leads, use the cleaner
[bare-lead wall-adapter diagram](../diagrams/huzzah32-wall-wart-wiring.svg).

## Known hardware

- Adafruit HUZZAH32 ESP32 Feather, product 3591, with headers installed
- WS2812-type 5 V strip labeled 60 LEDs/m
- 30 cm cut segment: 18 pixels
- Strip wire colors from the package: red `VCC`, white `GND`, green `DAT`
- 5 V USB wall adapter rated at least 1 A
- 330–470 ohm resistor
- 500–1000 microfarad electrolytic capacitor rated at least 6.3 V

## Wiring

| HUZZAH32 / component | Connects to |
|---|---|
| Micro-USB socket | 5 V USB wall adapter |
| `USB` pin | Strip red `VCC` wire |
| `GND` pin | Strip white `GND` wire |
| GPIO `14` | 330–470 ohm resistor, then strip green `DIN` wire |
| Capacitor `+` lead | Strip red `VCC`, near the strip input |
| Capacitor `-` lead/marked stripe | Strip white `GND`, near the strip input |

## Bare-lead 5 V wall-adapter option

Use this option only if the adapter label and a multimeter both confirm a
regulated **5.0 V DC** output. Do not infer polarity from wire color.

| Verified wall-adapter lead | Connects to |
|---|---|
| `+5 V` positive | HUZZAH32 `USB` pin **and** strip red `VCC` |
| `0 V` negative | HUZZAH32 `GND` **and** strip white `GND` |
| HUZZAH32 GPIO `14` | 330–470 ohm resistor, then strip green `DIN` |

Program the HUZZAH32 over Micro-USB first. Disconnect Micro-USB before applying
the bare-lead supply to the `USB` pin. Supplying external 5 V to that pin while
also connected to a computer can back-power the USB connection.

Connect to the strip's **input** end. Printed arrows must point away from the
HUZZAH32 and toward the later pixels.

## First power-up

1. Cut only at a marked copper cut line and verify the segment contains 18
   pixels.
2. Inspect every connection with power disconnected.
3. Confirm the electrolytic capacitor's polarity.
4. Configure firmware for 18 pixels on GPIO 14 and a maximum brightness of 10%
   for the first test.
5. Place the circuit on a nonconductive, nonflammable work surface.
6. Apply power from only one documented source. Do not have Micro-USB and the
   bare-lead supply connected at the same time.
7. Run solid cyan for 30 seconds, then disconnect power and check the strip,
   resistor, wires, and controller for unexpected warmth.

## Important logic-level note

The HUZZAH32 produces 3.3 V logic while the strip is powered at 5 V. A short
strip often works with this direct connection, but it is not the most robust
design. If pixels flicker, show incorrect colors, or ignore data, disconnect
power and add a 74AHCT125 or 74HCT245 level shifter. Do not compensate by
raising brightness.

## Do not

- Do not connect or power the full five-meter reel through the Feather.
- Do not connect the strip to the Feather's `3V` pin.
- Do not use the old swollen PKCELL battery.
- Do not wear the bench assembly.
- Do not leave the powered circuit unattended.

## Primary references

- [HUZZAH32 pinout](https://learn.adafruit.com/adafruit-huzzah32-esp32-feather/pinouts)
- [HUZZAH32 power management](https://learn.adafruit.com/adafruit-huzzah32-esp32-feather/power-management)
- [NeoPixel best practices](https://learn.adafruit.com/adafruit-neopixel-uberguide/best-practices)
- [NeoPixel powering guide](https://learn.adafruit.com/adafruit-neopixel-uberguide/powering-neopixels)

