[![Current Release](https://img.shields.io/github/release/scaarup/aula/all.svg?style=plastic)](https://github.com/scaarup/aula/releases) [![Github All Releases](https://img.shields.io/github/downloads/scaarup/aula/total.svg?style=plastic)](https://github.com/scaarup/aula/releases) [![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=plastic)](https://github.com/scaarup/aula)

# Aula

This is a custom component for Home Assistant to integrate Aula. It is very much based on the great work by @JBoye at https://github.com/JBoye/HA-Aula. However this "rewrite" comes with new features like:

- Installable/updatable via HACS
- "Ugeplaner"

  We save "ugeplaner" as sensor attributes "ugeplan" and "ugeplan_next". Can be rendered like:
  ```
  {{ state_attr("sensor.hojelse_skole_emilie", "ugeplan") }}
  ```
  
  And visualized in your dashboard with the markdown card:

  ```
  type: markdown
  content: '{{ state_attr("sensor.hojelse_skole_emilie", "ugeplan") }}'
  title: Ugeplan for Emilie
  ```
  Another example using vertical-stack and collapsable-cards:
  
  ![image](https://user-images.githubusercontent.com/8055470/200306258-1c9e98ff-75d9-4111-994c-a69833e40c61.png)

```
type: vertical-stack
cards:
  - type: custom:collapsable-cards
    title: Ugeplan Emilie
    cards:
      - type: markdown
        content: '{{ state_attr("sensor.hojelse_skole_emilie", "ugeplan") }}'
  - type: custom:collapsable-cards
    title: Ugeplan Emilie, næste uge
    cards:
      - type: markdown
        content: '{{ state_attr("sensor.hojelse_skole_emilie", "ugeplan_next") }}'
  - type: custom:collapsable-cards
    title: Ugeplan Rasmus
    cards:
      - type: markdown
        content: '{{ state_attr("sensor.hojelse_skole_rasmus", "ugeplan") }}'
  - type: custom:collapsable-cards
    title: Ugeplan Rasmus, næste uge
    cards:
      - type: markdown
        content: '{{ state_attr("sensor.hojelse_skole_rasmus", "ugeplan_next") }}'  
```
  
- School schedules as Home Assistant calendars. 
One calendar entity per child. Teacher initials are displayed and substitute teacher is highlighted with full name.

   ![image](https://user-images.githubusercontent.com/8055470/199254249-3bf441bc-7dce-4f5d-a809-d119d20a7b2b.png)
- Lots of small fixes and optimizations

## Installation

### HACS

- Add https://github.com/scaarup/aula as a custom repository
- Search for and install the "Aula" integration.
- Restart Home Assistant.

#### Manual installation

- Download the latest release.
- Unpack the release and copy the custom_components/aula directory into the custom_components directory of your Home Assistant installation.
- Restart Home Assistant.

## Setup

- Add the following to your configuration.yaml:

```
aula:
  username: <your unilogin username>
  password: <your unilogin password>
  schoolschedule: true # If you want "skoleskema" as calendars
```

- Restart Home Assistant.
