# V1: Straight-line shirt

V1 is the smallest useful wearable-lighting proof of concept: one removable,
diffused cyan light bar across the chest of an existing fitted black shirt.

## Scope

- One horizontal light bar, approximately 30 cm long
- Existing 5 V, 60 LED/m WS2812 strip: approximately 18 pixels
- Existing Adafruit HUZZAH32 ESP32 Feather for the bench prototype
- USB wall power for the first electrical and optical tests
- Removable non-stretch LED carrier
- Sewn fabric loops or sleeve; no adhesive directly on the stretch shirt
- Diffuser experiments at 5, 10, and 15 mm separation
- Controller and power source kept away from the chest and armpit

## Not part of V1

- Full five-meter strip
- Old PKCELL battery
- Custom PCB
- Permanent electronics sewn into the shirt
- Wi-Fi/Bluetooth phone interface
- Multiple lighting zones or animated garment patterns
- Final battery-powered public-wear configuration

## V1 success criteria

1. Eighteen pixels display stable cyan for at least 30 minutes on the bench.
2. Wiring, controller, and strip remain comfortably cool at the selected
   brightness.
3. The light reads as a reasonably continuous line at normal viewing distance.
4. The strip carrier can be removed without cutting stitches.
5. The shirt can stretch normally without pulling on the LED strip or wiring.
6. The physical build and measured current are documented before battery
   selection.

## Build order

1. Follow the repository's [USB bench test](../../docs/BENCH_TEST.md).
2. Record brightness, current, stability, and temperature observations.
3. Test available diffuser scraps over the powered strip without attaching
   anything to the shirt.
4. Make a removable non-stretch carrier.
5. Make a temporary fabric sleeve or three/four retaining loops.
6. Conduct an unpowered fit test.
7. Only after those steps, conduct a short supervised powered fit test.

## Project documents

- [Travel parts and packing checklist](PACKING_CHECKLIST.md)
- [HUZZAH32 wiring diagram](../../diagrams/huzzah32-neopixel-usb-wiring.html)
- [Bare-lead 5 V wall-adapter wiring diagram](../../diagrams/huzzah32-wall-wart-wiring.svg)
- [Bench-test procedure](../../docs/BENCH_TEST.md)
- [Safety requirements](../../docs/SAFETY.md)
- [Hardware inventory](../../docs/HARDWARE.md)

