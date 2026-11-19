# Wearable-electronics safety

This project places electrical conductors, a battery, and heat-producing
components near the body. Treat the garment as an engineering prototype.

## Batteries

- Use only a new, protected 3.7 V LiPo/Li-ion battery from a reputable source.
- Verify voltage, connector type, and polarity before connection.
- Never charge a battery while the garment is being worn.
- Remove the battery and all electronics before washing.
- Do not use a battery that is swollen, dented, punctured, wet, corroded,
  unusually warm, leaking, or producing an unusual odor.
- Do not put damaged lithium batteries in household trash, curbside recycling,
  or ordinary retail collection boxes. Contact a household hazardous-waste
  facility that accepts damaged lithium batteries.

## Electrical and thermal limits

- Test on a nonconductive, nonflammable surface before attaching anything to
  fabric.
- Enforce brightness and current limits in firmware; maxima are fault cases,
  not operating targets.
- Measure total current and component temperature during a sustained pattern.
- Fuse or otherwise protect the battery output against a short circuit.
- Insulate solder joints and exposed copper without trapping excessive heat.
- Provide strain relief where flexible wire meets a strip, connector, or PCB.
- Stop immediately for flicker, resets, odor, heat, discoloration, damaged
  insulation, or intermittent connections.

## Garment construction

- Keep rigid components away from the armpit, sternum, ribs, spine, waist
  pressure points, and groin.
- Place the controller and battery in separate removable pockets.
- Mount the LED strip on a non-stretch carrier so shirt stretch does not load
  the strip's copper traces.
- Use a removable connector between the chest light module and the side-seam
  wiring.
- Do not sew through a PCB, battery, wire, resistor, capacitor, connector, or
  LED strip.
- Do not operate the garment while wet or in rain.

## Testing progression

1. Controller alone over USB
2. Short LED segment at low brightness
3. Sustained bench test with current and temperature measurements
4. Removable textile carrier off the body
5. Unpowered fit test
6. Short supervised powered wear test

Do not skip directly from loose wiring to an unsupervised wearable assembly.

