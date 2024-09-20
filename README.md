# streamlit-ssh-config-editor

This is a naive example of .ssh/config file editor built using [streamlit.io](https://streamlit.io).


# build it

```bash
docker build -t ssh-config-editor .
```

# run it

This example mounts your current user .ssh config folder as readonly
```bash
docker run --rm -it \
  -u $(id -u):$(id -g) \
  -v $HOME/.ssh:/app/.ssh:ro \
  -p 8501:8501 \
  --name ssh-config-editor \
  ssh-config-editor
```

When you want to actually edit the file you can mount another path or remove the `:ro` flag.

> [!WARNING]
> 
> Please pay attention to avoid loosing your previous config 💣

# use it

Browse to http://0.0.0.0:8501