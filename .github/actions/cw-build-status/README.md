# CW Build Status Github Action

This action sends the status of a workflow step to CloudWatch Metrics.
It does this by checking the failure or success status of the previous workflow step
and sending that status to CloudWatch.  

This plugin should be used in conjunction with the [configure-aws-credentials Github Action][configure-aws-credentials] to setup your 
AWS credentials correctly. 

## Example Workflow

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    name: 'Build'
    steps:
    - name: Checkout repo
      uses: actions/checkout@v1
    - name: Configure AWS Credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-west-2
    - name: Build
      run: ./my-build-script.sh
    - name: Log Build Failure
      uses: ./.github/actions/cw-build-status/
      with:
        status: 'failure'
      if: failure() && github.ref == 'refs/heads/master'
    - name: Log Build Success
      uses: ./.github/actions/cw-build-status/
      with:
        status: 'success'
      if: success() && github.ref == 'refs/heads/master'
```

## CloudWatch Metrics format

The following metrics will be logged under the namespace `GithubCI` by default.
The namespace can be changed via the `namespace` input parameter.

- Builds - Always a value of 1
- FailedBuilds  - Value of 1 when the build fails, 0 otherwise
- SucceededBuilds - Value of 0 when the build fails, 1 otherwise

Each Metric has the following dimensions:

- IsCronJob - True if the workflow run is a `schedule`. False otherwise.
- ProjectName - Set to the input `project-name`.
  Defaults to [${{ github.repository }}].

## FAQ

**Q.** Can this send the status of multiple steps at once?
**A.** No, unfortunately you can only check the failure/success of the previous step, 
not multiple steps.
If you want to send the status of an entire workflow you could:
1. Create a new workflow that listens to a [check_run or check_suite webhook event][check-run-event-doc].
2. Query the Github API for the overall build status.
3. Send the status to CloudWatch Metrics.

## Inputs

### `status`

**Required** The build status `[failure|success]`.

### `namespace`

The namespace that metrics are logged to. Defaults to `GithubCI`.

### `project-name`

The name of your project. Defaults to [${{ github.repository }}]

[${{ github.repository }}]: https://help.github.com/en/actions/automating-your-workflow-with-github-actions/contexts-and-expression-syntax-for-github-actions#github-context
[configure-aws-credentials]: https://github.com/aws-actions/configure-aws-credentials
[check-run-event-doc]: https://developer.github.com/v3/activity/events/types/#checkrunevent
