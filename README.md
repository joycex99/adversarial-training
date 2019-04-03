# adversarial training

Follow set-up according to [mister_ed](https://github.com/revbucket/mister_ed). Some names, models, etc. modified, but most lib structure is the same.

E.g. to run PGD-based adversarial training:
```python -m scripts.advtrain_resnet32_pgd --exp resnet32_pgd --arch resnet32 --verbosity medium```