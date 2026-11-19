# Contributing

Thanks for helping improve the Light Fashion proof of concept.

## Before opening a change

1. Keep the wearable assembly removable and washable after electronics are
   removed.
2. Document the exact component, voltage, current limit, wire gauge, and
   connector polarity for electrical changes.
3. Include measured current and temperature results for anything intended to
   be worn.
4. Do not commit personal photos, Codex attachments, batteries of unknown
   provenance, credentials, build caches, or vendor downloads without a clear
   redistribution license.
5. Record the source and license of any third-party garment, model, texture,
   footprint, symbol, or 3D model.

## File expectations

- Preserve editable sources (`.blend`, `.py`, `.mmd`, and KiCad project files),
  not only screenshots or exports.
- Commit selected renders when they document an intentional design state.
- Do not commit Blender `.blend1` backups or generated fabrication folders.
- Keep physical hardware facts separate from conceptual Blender assumptions.

## Safety review

Any wearable-power change should address battery protection, overcurrent
protection, strain relief, insulation, maximum brightness/current in firmware,
charging procedure, removal before washing, and a stop condition for abnormal
heat, odor, swelling, flicker, or damage.

