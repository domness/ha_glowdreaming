# Scripts

These scripts are used to set various modes directly (prior to fully adding the entities):

## Calm Awake

```yaml
sequence:
  - alias: Medium Volume, No Light
    action: glowdreaming.set_mode
    metadata: {}
    data:
      light_effect: None
      brightness: None
      volume: Medium
      humidifier: None
    target:
      device_id: 3c0430c188e092e580e712f686a09db5
  - delay:
      hours: 0
      minutes: 0
      seconds: 10
      milliseconds: 0
  - alias: Low Volume, Awake Light (Low)
    action: glowdreaming.set_mode
    metadata: {}
    data:
      light_effect: Awake
      brightness: Low
      volume: Low
      humidifier: None
    target:
      device_id: 3c0430c188e092e580e712f686a09db5
  - delay:
      hours: 0
      minutes: 0
      seconds: 10
      milliseconds: 0
  - alias: No Sound, Awake Light (Medium)
    action: glowdreaming.set_mode
    metadata: {}
    data:
      light_effect: Awake
      brightness: Medium
      volume: None
      humidifier: None
    target:
      device_id: 3c0430c188e092e580e712f686a09db5
  - delay:
      hours: 0
      minutes: 0
      seconds: 10
      milliseconds: 0
  - alias: No Sound, Awake Light (Medium)
    action: glowdreaming.set_mode
    metadata: {}
    data:
      light_effect: Awake
      brightness: High
      volume: None
      humidifier: None
    target:
      device_id: 3c0430c188e092e580e712f686a09db5
alias: "Glow Dreaming: Calm Awake"
description: ""
icon: mdi:bell-sleep
```

## Daytime

```yaml
sequence:
  - action: glowdreaming.set_mode
    metadata: {}
    data:
      light_effect: Awake
      brightness: High
      volume: None
      humidifier: None
    target:
      device_id: 3c0430c188e092e580e712f686a09db5
alias: Glow Dreaming Daytime
description: ""
icon: mdi:cradle
```

## Night Change

```yaml
sequence:
  - action: glowdreaming.set_mode
    metadata: {}
    data:
      light_effect: Sleep
      brightness: Medium
      volume: High
      humidifier: None
    target:
      device_id: 3c0430c188e092e580e712f686a09db5
alias: Set Glow Dreaming to night change (red, noise)
description: ""
```

## Ready for Bed

```yaml
sequence:
  - action: glowdreaming.set_mode
    metadata: {}
    data:
      light_effect: Sleep
      brightness: High
      volume: Medium
      humidifier: None
    target:
      device_id: 3c0430c188e092e580e712f686a09db5
alias: Glow Dreaming Ready For Bed
description: ""
icon: mdi:cradle
```

## Sleep Mode

```yaml
sequence:
  - action: glowdreaming.set_mode
    metadata: {}
    data:
      light_effect: None
      brightness: None
      volume: High
      humidifier: None
    target:
      device_id: 3c0430c188e092e580e712f686a09db5
alias: Set Glow Dreaming for Sleep
description: ""
```

## Turn Off

```yaml
action: glowdreaming.set_mode
metadata: {}
data:
  light_effect: None
  brightness: None
  volume: None
  humidifier: None
target:
  device_id: 3c0430c188e092e580e712f686a09db5
```

## Refresh State

```yaml
sequence:
  - action: glowdreaming.refresh_state
    metadata: {}
    target:
      device_id: 3c0430c188e092e580e712f686a09db5
alias: Glowdreaming State
description: ""
```
