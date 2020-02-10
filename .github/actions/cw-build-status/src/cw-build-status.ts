import * as core from '@actions/core';
import CloudWatch from 'aws-sdk/clients/cloudwatch';
import * as github from '@actions/github'

const cloudwatch = new CloudWatch();
const context = github.context

const FAILED_BUILDS_METRIC_NAME = 'FailedBuilds'
const NUM_BUILDS_METRIC_NAME = 'Builds'
const SUCCESS_BUILDS_METRIC_NAME = 'SucceededBuilds'
const PROJECT_DIMENSION = 'ProjectName'
const IS_CRON_JOB_DIMENSION = 'IsCronJob'
const WORKFLOW_DIMENSION = 'WorkflowName'
const SUCCESS_METRIC_VALUE = 1.0
const FAILED_METRIC_VALUTE = 0.0

/**
 * Validate the `status` input to the action.
 * 
 * @param status The input string from the workflow
 */
function checkStatusString(status: string) {
  const validBuildStatusCheck = new RegExp('(success|failure)');
  if (!status.match(validBuildStatusCheck)) {
    throw new Error(`Invalid build status ${status} passed to cw-build-status`);
  }
}

/**
 * Construct a CloudWatch metric datum with repo and workflow info.
 * 
 * @param metricName The name of the CloudWatch Metric
 * @param projectName The name of the GitHub repo
 * @param isCronJob True if the workflow is a scheduled run. False otherwise.
 * @param value The value of the metric (1.0 or 0.0)
 */
function createMetricDatum(metricName, projectName, isCronJob, value) {
  const cronJobString = isCronJob ? 'True' : 'False'
  const metric_datum = { 'MetricName': metricName, 'Value': value, 
    'Dimensions': [ 
      { 'Name': PROJECT_DIMENSION, 'Value': projectName },
      { 'Name': IS_CRON_JOB_DIMENSION, 'Value': cronJobString },
      { 'Name': WORKFLOW_DIMENSION, 'Value': context.workflow }
    ] 
  } 
  return metric_datum
}

/**
 * Publish datapoints using the AWS CloudWatch Metrics SDK.
 * 
 * @param metricData A list of CloudWatch metric datapoints (objects)
 */
async function publishMetricData(metricData) {
  try {
    const metricNamespace = core.getInput('namespace');
    core.info(`Publishing metrics ${console.dir(metricData, {depth: false})} under namespace ${metricNamespace}`);
    await cloudwatch.putMetricData({
      Namespace: metricNamespace,
      MetricData: metricData
    }).promise();
  } catch (error) {
    core.error('Failed to publish metric data');
    core.setFailed(error.message);
  }
}

async function postBuildStatus() {
  try {
    // Get all parameters
    const projectName = core.getInput('project-name');
    const buildStatus = core.getInput('status', { required: true });
    checkStatusString(buildStatus);
    const isFailedBuild: Boolean = buildStatus === 'failure';
    const isCronJob: Boolean = context.eventName === 'schedule';

    // Populate the datapoints
    let metricData = [createMetricDatum(NUM_BUILDS_METRIC_NAME, projectName, isCronJob, SUCCESS_METRIC_VALUE)]
    metricData.push(
      createMetricDatum(FAILED_BUILDS_METRIC_NAME, projectName, isCronJob, isFailedBuild ? SUCCESS_METRIC_VALUE : FAILED_METRIC_VALUTE))
    metricData.push(
      createMetricDatum(SUCCESS_BUILDS_METRIC_NAME, projectName, isCronJob, isFailedBuild ? FAILED_METRIC_VALUTE : SUCCESS_METRIC_VALUE))

    // Log to CloudWatch
    await publishMetricData(metricData);
    core.info('Successfully published metrics');
  } catch (error) {
    core.setFailed(error.message);
  }
}

async function run() {
  await postBuildStatus();
}

run();
