# Templates

These are the example templates I currently use in my Home Assistant to feed data for the [glowdreaming_panels](./glowdreaming_panels.md).

## Brightness Sensor Template

```
{% if state_attr('sensor.glowdreaming_sensor', 'brightness') == 0 %}
  off
{% elif state_attr('sensor.glowdreaming_sensor', 'brightness') == 10 %}
  Low
{% elif state_attr('sensor.glowdreaming_sensor', 'brightness') == 40 %}
  Medium
{% elif state_attr('sensor.glowdreaming_sensor', 'brightness') == 100 %}
  High
{% else %}
  Unknown
{% endif %}
```

## Effect Template

```
{% if state_attr('sensor.glowdreaming_sensor', 'effect') == "Sleep" %}
  Low
{% elif state_attr('sensor.glowdreaming_sensor', 'effect') == "Awake" %}
  Medium
{% else %}
  Off
{% endif %}
```

## Light Template

```
{% if state_attr('sensor.glowdreaming_sensor', 'effect') == 'Sleep' %}
  {% if state_attr('sensor.glowdreaming_sensor', 'brightness') == 0 %}
    Sleep_Off
  {% elif state_attr('sensor.glowdreaming_sensor', 'brightness') == 10 %}
    Sleep_Low
  {% elif state_attr('sensor.glowdreaming_sensor', 'brightness') == 40 %}
    Sleep_Medium
  {% elif state_attr('sensor.glowdreaming_sensor', 'brightness') == 100 %}
    Sleep_High
  {% else %}
    Sleep_Off
  {% endif %}
{% elif state_attr('sensor.glowdreaming_sensor', 'effect') == 'Awake' %}
  {% if state_attr('sensor.glowdreaming_sensor', 'brightness') == 0 %}
    Awake_Off
  {% elif state_attr('sensor.glowdreaming_sensor', 'brightness') == 10 %}
    Awake_Low
  {% elif state_attr('sensor.glowdreaming_sensor', 'brightness') == 40 %}
    Awake_Medium
  {% elif state_attr('sensor.glowdreaming_sensor', 'brightness') == 100 %}
    Awake_High
  {% else %}
    Awake_Off
  {% endif %}
{% elif state_attr('sensor.glowdreaming_sensor', 'effect') == "None" %}
  {% if state_attr('sensor.glowdreaming_sensor', 'volume') == 1 %}
    SoundOnly_Low
  {% elif state_attr('sensor.glowdreaming_sensor', 'volume') == 2 %}
    SoundOnly_Medium
  {% elif state_attr('sensor.glowdreaming_sensor', 'volume') == 3 %}
    SoundOnly_High
  {% else %}
    Off
  {% endif %}
{% else %}
  Off
{% endif %}
```

## Scene Template

```
{% if
  state_attr('sensor.glowdreaming_sensor', 'effect') == "None" and
  state_attr('sensor.glowdreaming_sensor', 'brightness') == 0 and
  state_attr('sensor.glowdreaming_sensor', 'volume') == 3 %}
  sleep
{% elif
  state_attr('sensor.glowdreaming_sensor', 'effect') == "Sleep" and
  state_attr('sensor.glowdreaming_sensor', 'brightness') == 100 and
  state_attr('sensor.glowdreaming_sensor', 'volume') == 2 %}
  ready_for_bed
{% elif
  state_attr('sensor.glowdreaming_sensor', 'effect') == "Sleep" and
  state_attr('sensor.glowdreaming_sensor', 'brightness') == 40 and
  state_attr('sensor.glowdreaming_sensor', 'volume') == 3 %}
  night_change
{% elif
  state_attr('sensor.glowdreaming_sensor', 'effect') == "Awake" and
  state_attr('sensor.glowdreaming_sensor', 'brightness') == 100 and
  state_attr('sensor.glowdreaming_sensor', 'volume') == 0 %}
  daytime
{% else %}
  Off
{% endif %}
```

## Volume Template

```
{% if state_attr('sensor.glowdreaming_sensor', 'volume') == 0 %}
  off
{% elif state_attr('sensor.glowdreaming_sensor', 'volume') == 1 %}
  Low
{% elif state_attr('sensor.glowdreaming_sensor', 'volume') == 2 %}
  Medium
{% elif state_attr('sensor.glowdreaming_sensor', 'volume') == 3 %}
  High
{% else %}
  Unknown
{% endif %}
```
