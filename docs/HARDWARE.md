# Hardware inventory and design targets

## Hardware identified from the current inventory

### Adafruit HUZZAH32 ESP32 Feather

- Product label: Adafruit ESP32 Feather, product 3591
- Physical role: USB-powered bench controller
- Useful features: ESP32, Micro-USB programming, onboard 3.7/4.2 V LiPo charger
- Limitation: the installed headers and Feather footprint are bulky for a
  fitted garment

### Addressable LED strip

- Marking: WS2812-family addressable strip
- Supply: DC 5 V
- Density: 60 LEDs/m
- Reel length: 5 m
- Package power rating: 90 W for the entire reel
- Wire labeling: red `VCC`, white `GND`, green `DAT`
- Prototype segment: 30 cm, approximately 18 pixels

The full reel is not a wearable power load and must not be powered through the
Feather. At the common worst-case estimate of 60 mA per RGB pixel, 18 pixels
could draw about 1.08 A at full-brightness white before controller overhead.
Firmware must enforce a conservative brightness/current limit.

### Lonely Binary ESP32-WROOM-32UE boards

- USB-C development boards with external IPEX antennas
- Appropriate for bench development and juggling-club experiments
- No integrated wearable battery system is assumed
- Larger than the preferred final garment controller

### Retired PKCELL LiPo

- Marking: LP803860, 3.7 V, 2000 mAh
- Condition: more than five years without charging and visibly rounded/swollen
- Status: **do not charge, connect, test, transport casually, or use**
- Disposal: local household hazardous-waste service that explicitly accepts
  damaged lithium batteries

## Preferred wearable architecture

For a new build, use one of these controller directions:

- Seeed XIAO nRF52840 when Bluetooth control is enough and low power matters
- Seeed XIAO ESP32-C3 when Wi-Fi is required

The wearable power system should use a new protected 3.7 V LiPo from a
reputable vendor, verified connector polarity, a master disconnect, measured
current draw, overcurrent protection, strain relief, and separate removable
pockets for the controller and battery.

## Modeling-versus-hardware discrepancy

The current Blender generator models ten pixels at 30 LEDs/m and a XIAO-sized
controller. The bench hardware uses 18 pixels at 60 LEDs/m and a HUZZAH32.
This is intentional: the model explores fit while the bench setup establishes
electrical and optical behavior. Update the Blender assumptions only after the
bench results justify a final configuration.

