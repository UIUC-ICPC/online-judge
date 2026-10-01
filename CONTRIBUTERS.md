# contributers

add your name and discord handle here!

- Canchen Li (leaves333)
- Enya Chen (20oz)


## github instructions:

clone the repo:
```sh
git clone https://github.com/UIUC-ICPC/online-judge.git
```

go into the repo, and checkout the `contributing` branch
```sh
cd online-judge
git checkout contributing
```

create a new branch based off of this contributing branch, then switch to your
new branch:
```sh
git branch your-branch-name
git checkout new-branch
```

edit this `CONTRIBUTERS.md` file to include your info, then add and commit your
changes:
```sh
git add CONTRIBUTERS.md
git commit -m "your commit message here!"
git push
```

create a pull request (pr)
after you push to main, head to the github website (there is no "git pull request" command)
on github, within your new branch with your changes, there will be an option to "Contribute" and make a Pull Request
- on your pull request you can add details (what your pull request is about, etc)
- before it can be pushed to main, it will need an approval from someone else
- after approval, it can then be merged into our main branch
