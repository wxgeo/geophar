Build and run container
=======================

# Goal
Currently, containers are used only to test geophar in a different environment, and not for deployment (though it would be quite easy to adapt it).

To generate and manage containers, we will used `Podman`, which is like `Docker` (same commands), 
but can be used as a normal user (no need for `root` permissions).

# Before starting

To install `Podman`:
```
    sudo apt install podman containers-storage
```

The package `containers-storage`, though not mandatory, is strongly advised to accelerate greatly images generation.

To verify the installation, you may execute `podman info | grep graphDriverName`, which should return `overlay` (and not `vfs`, which is default value).

To use Docker repositories, we must now configure containers registries:

```
    mkdir ~/.config/containers/
    echo 'unqualified-search-registries = ["docker.io"]' >> ~/.config/containers/registries.conf
```

# Create an image

Thanks to the `Makefile`, you just have to run:

```
    make build
```

You may of course modify the `Dockerfile` first if needed.


# Run a container

Just execute:

```
    make run
```


