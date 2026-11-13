---
name: yaml-mixed
description: An earlier unsafe yaml.load must not be hidden by a later SafeLoader call.
---
yaml.load(blob)
yaml.load(other, Loader=yaml.SafeLoader)
