---
name: Urban Environment Observation System
description: A daylight environmental observatory shaped by station plots, transects, and traceable measurement time.
---

<!-- SEED: established with the user before implementation; re-run $impeccable document once there's code to capture the actual tokens and components. -->

# Overview

**Creative North Star: “The city as an instrument reading.”**

The interface behaves like a contemporary environmental observatory. It borrows the discipline of meteorological station plots and field transects—measured coordinates, sample time, fine rules and annotated values—without imitating a scientific terminal. The main surface is quiet mineral daylight; observed values carry the visual weight.

The reusable signature is the **Observation Glyph**: a compact SVG instrument whose rings encode humidity and AQI while adjacent marks report precipitation, wind and pressure. It only uses values present in the selected observation. A thin observation line connects data time, city and pipeline provenance across pages.

**Key Characteristics:**

- asymmetric, task-led page composition instead of repeated card grids;
- paper-like surfaces separated by rules or whitespace, with shadows reserved for overlays;
- Chinese-first labels with tabular figures for measurements;
- measured cyan and lichen green for interaction; AQI colors remain semantic;
- subtle route and state transitions, never continuous ambient animation.

**The Observation-Time Rule.** Every headline measurement is paired with its actual observation time and never described as real-time unless the source proves it.

**The One-Instrument Rule.** Each viewport has one dominant visual instrument; secondary metrics support it rather than becoming equal cards.

# Colors

- **Mineral fog** (`#F2F5F2`) is the application ground.
- **Observation paper** (`#FCFDFB`) holds primary content.
- **Deep estuary** (`#142821`) is the principal text and high-contrast line color.
- **Instrument green** (`#1F6B57`) marks active navigation and actions.
- **Atmosphere cyan** (`#287F91`) carries weather series and focus.
- **Solar ochre** (`#C47A24`) highlights attention without becoming a general CTA color.
- **Boundary line** (`#D7E0DB`) separates dense engineering information.
- **Muted moss** (`#5E7169`) supports metadata while preserving AA contrast.
- AQI states use named green, yellow, orange, red and violet pairs with text labels.

**The Semantic-Color Rule.** AQI, quality and failure colors are never decorative and never communicate alone.

# Typography

Use one humanist UI family for Chinese and Latin interface text, with the system CJK sans fallback. Measurement values use tabular figures. A restrained monospace is reserved for timestamps, run IDs and watermarks—not headings.

- Display: 40/44 desktop, 32/36 compact; weight 650.
- H1: 28/34; weight 650.
- H2: 21/28; weight 620.
- Body: 16/25.
- Label: 13/18; weight 620.
- Data: 28–64 with `font-variant-numeric: tabular-nums`.

**The Unit-Breath Rule.** Values and units have a deliberate small gap: `20.4 °C`, `12.8 μg/m³`.

# Layout

Desktop uses a 248px navigation rail and a maximum 1480px content field. The content grid has twelve columns with 24px gutters; major sections use 32–48px vertical rhythm. Tablet collapses the rail to a top bar. Mobile uses a top title bar and a five-item bottom navigation with secondary destinations in a menu.

Overview is built around an asymmetric observation field, city rail and map. City Detail follows a vertical time transect. Comparison uses a control bench plus ranked chart and matrix. Quality resembles a diagnostic worksheet. Pipeline is a left-to-right process track. About is a readable technical document.

**The Task-Shape Rule.** Pages share tokens and controls, not identical section templates.

# Elevation & Depth

Primary content uses surface contrast and one-pixel rules. Only menus, tooltips and the mobile drawer use soft offset shadows. The weather observation field may use a low-contrast atmospheric wash derived from measured temperature range, but never a site-wide gradient.

# Shapes

Default surfaces use 12px corners; dense tables and controls use 8px; small status badges may use a full pill. Observation glyphs, map markers and AQI dots are circular because they represent measurements, not because every component is rounded.

# Do's and Don'ts

## Do

- show source, unit, granularity and observation time;
- use one clear chart question per visual;
- provide chart summaries and table alternatives;
- keep controls at least 44px high on touch surfaces;
- preserve direct links, browser history and keyboard focus.

## Don't

- label archived observations as current conditions;
- fabricate weather condition icons when `weather_code` is unavailable;
- nest cards, repeat mechanical KPI grids or decorate headings with eyebrows;
- use glassmorphism, purple gradients, particles or continuously moving backgrounds;
- expose internal field names such as `timestamp`, `metric` or `value` to users.
