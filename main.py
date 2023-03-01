import pandas as pd
import numpy as np
import streamlit as st
from scipy.stats.mstats import winsorize
import plotly.express as px
import plotly.graph_objects as go


# load the main data and cache it.
@st.cache_data()
def load_data() -> pd.DataFrame:
    return pd.read_pickle('input/data.pkl.gz')


# preparation of figure 4 of the paper
def figure_four_presentation():
    st.header("Figure 4")
    figure_four = go.Figure(data=[go.Scatter(x=pct_data['price_percentiles'],  # EPS scatter plot
                                             y=pct_data['eps'],
                                             mode='markers',
                                             name='EPS',
                                             hovertemplate='¢ %{y:.2f}',
                                             marker=dict(symbol='diamond', color='#89C5C1')
                                             ),
                                  go.Scatter(x=pct_data['price_percentiles'],  # forecast error scatter plot
                                             y=pct_data['ferr'],
                                             mode='markers',
                                             name='FERR',
                                             hovertemplate='¢ %{y:.2f}',
                                             marker=dict(symbol='square', color='#C5C189')
                                             ),
                                  go.Scatter(x=pct_data['price_percentiles'],  # Change in EPS scatter plot
                                             y=pct_data['cheps'],
                                             mode='markers',
                                             name='∆EPS',
                                             hovertemplate='¢ %{y:.2f}',
                                             marker=dict(symbol='triangle-up', color='#C189C5')
                                             ),
                                  go.Scatter(x=pct_data['price_percentiles'],  # IQR of EPS scatter plot
                                             y=pct_data['iqr_eps'],
                                             mode='markers',
                                             name='IQR EPS',
                                             hovertemplate='¢ %{y:.2f}',
                                             marker=dict(symbol='diamond-open', color='#89C5C1'),
                                             ),
                                  go.Scatter(x=pct_data['price_percentiles'],
                                             y=pct_data['iqr_ferr'],
                                             mode='markers',
                                             name='IQR FERR',
                                             hovertemplate='¢ %{y:.2f}',
                                             marker=dict(symbol='square-open', color='#C5C189')
                                             ),
                                  go.Scatter(x=pct_data['price_percentiles'],
                                             y=pct_data['iqr_cheps'],
                                             mode='markers',
                                             name='IQR ∆EPS',
                                             hovertemplate='¢ %{y:.2f}',
                                             marker=dict(symbol='triangle-up-open', color='#C189C5')
                                             )
                                  ],
                            layout=dict(hovermode='x unified',
                                        title=dict(text='<b>Medians and interquartile ranges for EPS, FERR, and ∆EPS '
                                                        'as a function of centiles of price per share</b>',
                                                   font=dict(family='Helvetica',
                                                             size=12,
                                                             ),
                                                   x=0.5,
                                                   xanchor='center',
                                                   yanchor='middle',
                                                   ),
                                        height=700,
                                        paper_bgcolor='#fff',
                                        plot_bgcolor='#fafafa',
                                        legend=dict(title='<b>Median of:</b>',
                                                    itemclick='toggleothers',
                                                    yanchor='top', y=0.99,
                                                    xanchor="left", x=0.01
                                                    ),
                                        ),
                            layout_yaxis_range=[-10, 100],
                            layout_xaxis_range=[0, 100],
                            )
    figure_four.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#cfcaca')
    figure_four.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#cfcaca')
    figure_four.update_layout(xaxis={'title': 'Centile of Price'},
                              yaxis={'title': 'Cents per Share: Median: IQR'})
    st.plotly_chart(figure_four)


# preparation of Figure 5 of the paper
def figure_five_presentation(figure_five_data: pd.DataFrame) -> None:
    figure_five_data.dropna(axis=0, subset=['cheps'], inplace=True)
    figure_five_data = figure_five_data[(figure_five_data['cheps'] >= -20) & (figure_five_data['cheps'] <= 20)]
    st.header("Figure 5")
    figure_five = go.Figure(data=[go.Histogram(x=figure_five_data['cheps'],
                                               hoverinfo='all',
                                               name='',
                                               hovertemplate="<b>∆EPS range:</b> %{x} cents<br>"
                                                             "<b>Freq:</b> %{y:,}",
                                               showlegend=False,
                                               xbins={'start': -20, 'size': 1, 'end': 20},
                                               marker=dict(color='#C189C5',
                                                           line=dict(color='#fff', width=0.1),
                                                           opacity=(.5, .5, .5, .5, .5, .5, .5, .5, .5, .5,
                                                                    .5, .5, .5, .5, .5, .5, .5, .5, .5, .5, 1)
                                                           ),
                                               hoverlabel=dict(bgcolor='#fafafa'),
                                               selected=dict(marker={'opacity': 1}),
                                               unselected=dict(marker={'opacity': 0.7}))],
                            layout=dict(title=dict(text='<b>Histogram of change in EPS '
                                                        '(∆EPS = EPS<sub>t</sub> - EPS<sub>t-4</sub>):<br>'
                                                        'exploring the threshold of "sustain recent performance."</b>',
                                                   font=dict(family='Helvetica', size=12),
                                                   x=0.5,
                                                   xanchor='center',
                                                   yanchor='middle'
                                                   ),
                                        clickmode='select',
                                        plot_bgcolor='#fafafa'
                                        )
                            )
    figure_five.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#cfcaca')

    st.plotly_chart(figure_five)


# preparation of Figure 6 of the paper
def figure_six_presentation(figure_six_data: pd.DataFrame) -> None:
    figure_six_data.dropna(axis=0, subset=['ferr'], inplace=True)
    figure_six_data = figure_six_data[(figure_six_data['ferr'] >= -20) & (figure_six_data['ferr'] <= 20)]
    st.header("Figure 6")
    figure_six = go.Figure(data=[go.Histogram(x=figure_six_data['ferr'],
                                              hoverinfo='all',
                                              name='',
                                              hovertemplate="<b>Forecast Error range:</b> %{x} cents<br>"
                                                            "<b>Freq:</b> %{y:,}",
                                              showlegend=False,
                                              xbins={'start': -20, 'size': 1, 'end': 20},
                                              marker=dict(color='#C5C189',
                                                          line=dict(color='#fff', width=0.1),
                                                          opacity=(.5, .5, .5, .5, .5, .5, .5, .5, .5, .5,
                                                                   .5, .5, .5, .5, .5, .5, .5, .5, .5, .5, 1)
                                                          ),
                                              hoverlabel=dict(bgcolor='#fafafa'),
                                              selected=dict(marker={'opacity': 1}),
                                              unselected=dict(marker={'opacity': 0.7}))],
                           layout=dict(title=dict(text="<b>Histogram of forecast error for earnings per share:<br>"
                                                       "exploring the threshold of meeting analysts’ expectations.</b>",
                                                  font=dict(family='Helvetica', size=12),
                                                  x=0.5,
                                                  xanchor='center',
                                                  yanchor='middle'
                                                  ),
                                       clickmode='select',
                                       plot_bgcolor='#fafafa'
                                       )
                           )
    figure_six.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#cfcaca')

    st.plotly_chart(figure_six)


# preparation of Figure 7 of the paper
def figure_seven_presentation(figure_seven_data: pd.DataFrame) -> None:
    figure_seven_data.dropna(axis=0, subset=['eps'], inplace=True)
    figure_seven_data = figure_seven_data[(figure_seven_data['eps'] >= -20) & (figure_seven_data['eps'] <= 20)]
    st.header("Figure 7")
    figure_seven = go.Figure(data=[go.Histogram(x=figure_seven_data['eps'],
                                                hoverinfo='all',
                                                name='',
                                                hovertemplate="<b>Forecast Error range:</b> %{x} cents<br>"
                                                              "<b>Freq:</b> %{y:,}",
                                                showlegend=False,
                                                xbins={'start': -20, 'size': 1, 'end': 20},
                                                marker=dict(color='#89C5C1',
                                                            line=dict(color='#fff', width=0.1),
                                                            opacity=(.5, .5, .5, .5, .5, .5, .5, .5, .5, .5,
                                                                     .5, .5, .5, .5, .5, .5, .5, .5, .5, .5, 1)
                                                            ),
                                                hoverlabel=dict(bgcolor='#fafafa'),
                                                selected=dict(marker={'opacity': 1}),
                                                unselected=dict(marker={'opacity': 0.7}))],
                             layout=dict(title=dict(text='<b>Histogram of EPS:<br>'
                                                         'exploring the threshold of "positive/zero profit."</b>',
                                                    font=dict(family='Helvetica', size=12),
                                                    x=0.5,
                                                    xanchor='center',
                                                    yanchor='middle'
                                                    ),
                                         clickmode='select',
                                         plot_bgcolor='#fafafa'
                                         )
                             )
    figure_seven.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#cfcaca')

    st.plotly_chart(figure_seven)


if __name__ == "__main__":
    # paper information
    st.header("Earnings Management to Exceed Thresholds")
    st.caption("François Degeorge, Jayendu Patel, and Richard Zeckhauser")
    st.caption("*The Journal of Business*, Vol. 72, No. 1 (January 1999), pp. 1-33")
    st.caption("[Link to the original article](https://www.jstor.org/stable/10.1086/209601)")

    # open the data
    df = load_data()

    # save user selection of the years to include in the replication
    with st.expander(label='Expand to change the parameters of the study', expanded=True):
        st.subheader('Parameters of the Study')

        # user chooses the years of the sample period
        st.subheader('Year')
        st.write('Degeorge et al. (1999) sample covers 1974 to 1996. '
                 'Due to limited access to historical data, the sample '
                 'for this replication starts from 1984, '
                 'which is the first year available on I/B/E/S. '
                 'The default settings cover only the years'
                 'that overlap with the original study (1984 to 1996).\n\n'
                 'Try expanding the sample period using the slider below!')
        st.session_state.selected_date = st.slider(label='Range of years:',
                                                   min_value=min(df['year']),
                                                   max_value=max(df['year']),
                                                   value=[1984, 1996])

        # user chooses the cutoff for extreme prices
        st.subheader('Extreme Price cutoffs')
        st.write('In their study, Degeorge et al. (1999) did not normalize any of their variables '
                 '(***EPS***, Analyst\'s Forecast Error (***FERR***), '
                 'and Change in EPS from a year ago (***∆EPS***). '
                 'The reason for their decision was that ***"spurious patterns '
                 'can arise in the distribution of such normalized EPS."*** '
                 '(Dageorge et al. 1999; Page 16).\n\n'
                 'Instead, they excluded firms with extreme prices. '
                 'Based on the distribution of ***EPS***, ***FERR***, '
                 'and ***∆EPS*** shown in [Figure 4](#figure-4). '
                 'This replication has a cutoff of 10% (just like the original study).\n\n'
                 'However, you still have the choice to change the cutoff and see what happens!'
                 )
        st.session_state.selected_cutoff = st.slider(label='Cutoff Percentile:',
                                                     min_value=0,
                                                     max_value=100,
                                                     value=[10, 90])

        # use winsorized or unwinsorized values based on the preference of the user
        st.session_state.use_winsorized = st.checkbox(label='Use Winsorized Variables (1% , 99%)',
                                                      value=False)

    # restrict the data range to the selected years
    df = df[(df['year'] >= st.session_state.selected_date[0]) & (df['year'] <= st.session_state.selected_date[1])]
    df.reset_index(inplace=True)

    if st.session_state.use_winsorized:
        for column in ['eps', 'ferr', 'cheps']:
            df[f'{column}'] = df[f'{column}_w']

    else:
        for column in ['eps', 'ferr', 'cheps']:
            df[f'{column}'] = df[f'{column}_n']

    # create price percentiles after applying date restrictions and winsorization.
    # first step to recreate Figure 4 of Degeorge et al., 1999
    df['price_percentiles'] = df['price'].rank(pct=True).round(decimals=2) * 100

    medians_by_PCT = df.groupby('price_percentiles',
                                as_index=False).median(['eps', 'ferr', 'cheps'])

    p25_by_PCT = df[['price_percentiles', 'eps', 'ferr', 'cheps']].groupby('price_percentiles',
                                                                           as_index=False).quantile(q=0.25)

    p75_by_PCT = df[['price_percentiles', 'eps', 'ferr', 'cheps']].groupby('price_percentiles',
                                                                           as_index=False).quantile(q=0.75)

    pct_data = medians_by_PCT.join(p25_by_PCT, rsuffix='_P25')
    pct_data = pct_data.join(p75_by_PCT, rsuffix='_P75')

    pct_data['iqr_eps'] = (pct_data['eps_P75'] - pct_data['eps_P25'])
    pct_data['iqr_ferr'] = (pct_data['ferr_P75'] - pct_data['ferr_P25'])
    pct_data['iqr_cheps'] = (pct_data['cheps_P75'] - pct_data['cheps_P25'])

    # TODO: Do we need vintage data to exactly replicate the study?

    histogram_data: pd.DataFrame = df[(df['price_percentiles'] >= st.session_state.selected_cutoff[0]) &
                                      (df['price_percentiles'] <= st.session_state.selected_cutoff[1])]

    # present figure four
    figure_four_presentation()

    # present figure five
    figure_five_presentation(histogram_data)

    # present figure six
    figure_six_presentation(histogram_data)

    # present figure seven
    figure_seven_presentation(histogram_data)
