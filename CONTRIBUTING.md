# Contributor guidelines

## Version control

Git is the versioning system for this project. We use git-flow in order to separate features from ongoing development work.
That means that the main branch for new code is `develop`, and the most recent release can be built from `master`.

## Feature branches

The high-level features we'd like to work on next are listed in [the TODO file](./TODO.md).
Actually working on these may require further discussion, for which you're welcome to ping `@blagae` in tickets or pull requests.

For unfinished feature development, please use the feature branch concept from git-flow.

The use of feature branches is not necessary for small bug fixes, enhancements, documentation,
and other work items which can be easily contained in a single commit.

## Pull Requests

### Bug fixes

When submitting a bug fix in a pull request, you should include tests that would fail without your bugfix.
This will serve as documentation for the original problem, and may be the deciding argument convincing us that there is a problem.

Ideally, your pull request consists of at least two commits (in this order):

1. in the first commit: the failing tests, so that reproducing the problem can be done by checking out this commit
2. (optional) any intermediate steps for the fix
3. in the last commit: the code for the full fix, which makes the tests succeed

Of course, this requires some discipline and more planning than you may be used to.
Compliance with this rule is strongly encouraged, but is not required for a fix to be accepted.

### Tests

Feature requests or bug reports may come in the form of pull requests containing failing tests. However, these will not be picked up
with priority unless they demonstrate that existing functionality is terribly broken. They will also only be picked up in
feature or hotfix branches, in order not to muddy up the develop branch.

We hope to be able to do a test coverage analysis soon, which will probably reveal a few huge coverage gaps which must be fixed.

## Code style

While Elisio is not exactly a paragon of Python writing style, we are making efforts to write decently readable
and Pythonic code where possible. Contributors needn't feel obligated to clean up all existing code, but should at
least make an effort to not make the current situation worse.

You are also welcome to point out bad practices or code smells.

## Version numbering

As of December 2016, no releases have been made. We intend to implement Semantic Versioning when we do.
