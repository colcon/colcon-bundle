import {checkStatusString, createMetricDatum, publishMetricData} from '../src/cw-build-status'
import CloudWatch from 'aws-sdk/clients/cloudwatch'

jest.mock('aws-sdk/clients/cloudwatch')

describe('unit test suite', () => {

  test('checkStatusString passes on valid success string', async () => {
      expect(() => {
        checkStatusString('success')
      }).not.toThrow()
  });

  test('checkStatusString throws on invalid status string', async () => {
    expect(() => {
      checkStatusString('foo')
    }).toThrow()
  });

  test('createMetricDatum returns valid datum', async () => {
    const metricName = 'MyMetric'
    const projectName = 'MyProject'
    const isCronJob = true
    const value = 1.0
    const result = createMetricDatum(metricName, projectName, isCronJob, value)
    expect(result.MetricName).toStrictEqual(metricName)
    expect(result.Value).toStrictEqual(value)
    expect(result.Dimensions.length).toStrictEqual(2)
  });

  test('publishMetricData calls SDK', async () => {
    CloudWatch.prototype.putMetricData = jest.fn().mockImplementationOnce(() => {
      return {
        promise() {
          return Promise.resolve({
            data: 'success'
          })
        }
      }
    })

    const metricNamespace = 'MyNamespace'
    const metricName = 'MyMetric'
    const projectName = 'MyProject'
    const isCronJob = true
    const value = 1.0
    const datum = createMetricDatum(metricName, projectName, isCronJob, value)
    const metricData = [datum]
    publishMetricData(metricNamespace, metricData)
    expect(CloudWatch.prototype.putMetricData).toBeCalled()
  })
})
